#!/bin/bash
# Substack Article Generator
# Reads a seed file, extracts source material from books, generates a Substack-optimized article
# Usage: ./generate-article.sh <seed-file>

set -euo pipefail

SEED_FILE="${1:?Usage: ./generate-article.sh <seed-file>}"
SUBSTACK_DIR="$(cd "$(dirname "$0")" && pwd)"
BOOKS_DIR="$HOME/Projects/books"
DRAFTS_DIR="$SUBSTACK_DIR/Drafts"

if [[ ! -f "$SEED_FILE" ]]; then
    echo "Error: Seed file not found: $SEED_FILE"
    exit 1
fi

# Extract metadata from seed file
TITLE=$(grep "^title:" "$SEED_FILE" | sed 's/^title: *"//' | sed 's/"$//')
TYPE=$(grep "^type:" "$SEED_FILE" | sed 's/^type: *//')
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
DRAFT_FILE="$DRAFTS_DIR/${SLUG}.md"

echo "=== Substack Article Generator ==="
echo "Seed:  $SEED_FILE"
echo "Title: $TITLE"
echo "Type:  $TYPE"
echo "Draft: $DRAFT_FILE"
echo ""

# Read the full seed content
SEED_CONTENT=$(cat "$SEED_FILE")

# Build the prompt based on article type
case "$TYPE" in
    reframe)
        ARTICLE_INSTRUCTIONS="Write a REFRAME article. Open with recognizable pain language. Name what the reader is experiencing. Deliver the structural reframe. Close with a single structural insight — not advice. 800-1200 words."
        ;;
    concept)
        ARTICLE_INSTRUCTIONS="Write a CONCEPT ESSAY. Name the concept clearly. Ground it in observable behavior. One or two examples. End with the structural distinction. 600-1000 words."
        ;;
    case-read)
        ARTICLE_INSTRUCTIONS="Write a CASE READ. Open with a recognizable scenario. Walk through the surface reading. Then walk through the structural read. Close with the distinction. 800-1200 words."
        ;;
    cross-domain)
        ARTICLE_INSTRUCTIONS="Write a CROSS-DOMAIN BRIDGE. Name both domains. Show the same pattern operating in both. Name why the connection matters. 600-1000 words."
        ;;
    *)
        ARTICLE_INSTRUCTIONS="Write a Substack article based on the seed content. 600-1200 words."
        ;;
esac

# Collect source book excerpts
echo "Extracting source material from books..."
SOURCE_MATERIAL=""
while IFS= read -r book; do
    book=$(echo "$book" | tr -d ' "' | tr -d "'")
    case "$book" in
        heroes-not-required)
            BOOK_PATH="$BOOKS_DIR/structure/heroes-not-required/EN/Drafts/HEROES_NOT_REQUIRED_FINAL_v2.1.md"
            ;;
        bottleneck-trap)
            BOOK_PATH="$BOOKS_DIR/structure/bottleneck-trap/bottleneck-trap-pub08.md"
            ;;
        built-to-need-you)
            BOOK_PATH="$BOOKS_DIR/structure/built-to-need-you/built-to-need-you-combined.md"
            ;;
        how-did-this-become-my-job)
            BOOK_PATH="$BOOKS_DIR/structure/how-did-this-become-my-job/hdtbmj-combined.md"
            ;;
        its-not-that-complicated)
            BOOK_PATH="$BOOKS_DIR/structure/its-not-that-complicated/its-not-that-complicated.md"
            ;;
        when-we-stop-seeing-people)
            BOOK_PATH="$BOOKS_DIR/structure/when-we-stop-seeing-people/EN/Drafts/WWSSP DRAFT 7.md"
            ;;
        renergence)
            BOOK_PATH="$BOOKS_DIR/renergence/renergence/EN/Drafts/Renergence FINAL DRAFT for French Translaiton Feb 4 .md"
            ;;
        engagement-map)
            BOOK_PATH="$BOOKS_DIR/engagement/engagement-map/EN/Drafts/ENGAGEMENT MAP BOOK 7-for-vellum.md"
            ;;
        on-witnessing)
            BOOK_PATH="$BOOKS_DIR/engagement/on-witnessing/EN/Drafts/ON WITNESSING DRAFT FINAL.md"
            ;;
        engagement-governed-practice)
            BOOK_PATH="$BOOKS_DIR/engagement/engagement-governed-practice/EN/Drafts/Engagement as a Governed Practice An Ontology of Attending and Responding.md"
            ;;
        orientation)
            BOOK_PATH="$BOOKS_DIR/engagement/orientation/EN/Drafts/ORIENTATION DRAFT 1.md"
            ;;
        multiple-natures)
            BOOK_PATH="$BOOKS_DIR/multiple-natures/multiple-natures/EN/Drafts/MN Book Draft 1.0.md"
            ;;
        inevitability)
            BOOK_PATH="$BOOKS_DIR/_cross-cutting/perception/Perception Series - Latest (Deprecated)/Inevitability - Final Draft.md"
            ;;
        lenses)
            BOOK_PATH="$BOOKS_DIR/_cross-cutting/perception/Perception Series - Latest (Deprecated)/Lenses - Final Draft.md"
            ;;
        witness)
            BOOK_PATH="$BOOKS_DIR/_cross-cutting/perception/Perception Series - Latest (Deprecated)/Witness - Final Draft.md"
            ;;
        constraint)
            BOOK_PATH="$BOOKS_DIR/_cross-cutting/perception/Perception Series - Latest (Deprecated)/Constraint - Final Draft.md"
            ;;
        *)
            echo "  Warning: Unknown book '$book', skipping"
            continue
            ;;
    esac

    if [[ -f "$BOOK_PATH" ]]; then
        echo "  Reading: $book"
        # Take first 4000 chars as context (enough for key concepts)
        EXCERPT=$(head -c 4000 "$BOOK_PATH")
        SOURCE_MATERIAL="$SOURCE_MATERIAL

--- SOURCE: $book ---
$EXCERPT
--- END SOURCE ---
"
    else
        echo "  Warning: Book not found at $BOOK_PATH"
    fi
done < <(grep -A 20 "^source_books:" "$SEED_FILE" | grep "^  -" | sed 's/^  - //')

echo ""
echo "Generating article via Claude Code..."

# Generate the article using Claude Code
claude -p "You are Steven Rudolph's writing assistant. Generate a Substack article based on this seed and source material.

ARTICLE SEED:
$SEED_CONTENT

SOURCE MATERIAL FROM BOOKS:
$SOURCE_MATERIAL

INSTRUCTIONS:
$ARTICLE_INSTRUCTIONS

VOICE RULES:
- Write in Steven's voice: direct, structural, no self-help tone
- No rhetorical questions as hooks
- No 'In this article, I'll...'
- No listicles
- Assertions, not suggestions
- The reader is treated as intelligent and already experiencing the pattern
- Pain language as entry point, structural language as reframe
- End with a single thought, not a call to action

FORMAT:
- Start with the title as H1
- Subtitle as italics on the next line
- Then the article body
- No header images or graphics references
- Use --- for section breaks if needed

SUBSTACK OPTIMIZATION:
- Title: 6-10 words, pain-language first
- Opening line: land immediately in recognizable experience
- Length: target the word count specified above
- End with a single resonant thought" > "$DRAFT_FILE"

echo ""
echo "=== Article generated ==="
echo "Draft saved to: $DRAFT_FILE"
echo ""
echo "Next steps:"
echo "  1. Review and edit the draft"
echo "  2. Move to Reviewed/ when ready"
echo "  3. Publish to Substack"
