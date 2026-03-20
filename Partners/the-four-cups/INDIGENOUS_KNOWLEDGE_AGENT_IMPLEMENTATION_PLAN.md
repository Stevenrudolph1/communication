# Indigenous Knowledge Agent Integration - Complete Implementation Plan

**Project:** The Four Cups - Indigenous Knowledge Agent  
**Date:** 2025-01-XX  
**Status:** Planning Phase  
**Priority:** High - Strategic Partnership Feature

---

## Executive Summary

This document outlines a complete plan for integrating indigenous knowledge into the XaviAgent system as a collaborative agent that works alongside users' personal agents. This approach honors indigenous wisdom traditions as distinct, authoritative voices while leveraging XaviAgent's existing multi-agent orchestration architecture.

**Key Decision:** Implement as **collaborative agent team** (Option 2) rather than adding indigenous knowledge as a feature to existing agents. This ensures cultural respect, technical scalability, and authentic integration.

---

## Table of Contents

1. [Vision & Philosophy](#vision--philosophy)
2. [Architecture Overview](#architecture-overview)
3. [Cultural Considerations](#cultural-considerations)
4. [Technical Implementation](#technical-implementation)
5. [Database Schema](#database-schema)
6. [API Design](#api-design)
7. [Frontend Integration](#frontend-integration)
8. [Implementation Phases](#implementation-phases)
9. [Testing Strategy](#testing-strategy)
10. [Rollout Plan](#rollout-plan)
11. [Success Metrics](#success-metrics)
12. [Risk Mitigation](#risk-mitigation)

---

## Vision & Philosophy

### The Core Concept

**Two agents, one conversation:**
- **Personal Agent (Xavi):** Uses MN/AD/AQ framework, personal coaching style, user's goals
- **Indigenous Knowledge Agent:** Brings wisdom from indigenous traditions, community perspective, land/relationship awareness

**Together they provide:**
- Multiple perspectives on the same question
- Complementary insights (personal + communal)
- Cultural learning opportunities
- Richer, more holistic guidance

### Why This Approach

**1. Cultural Respect**
- Indigenous knowledge is not a "feature" but a distinct way of knowing
- Separate agent honors its authority and uniqueness
- Can be curated and controlled by indigenous knowledge keepers

**2. Technical Alignment**
- Leverages existing multi-agent orchestration
- Framework Engine architecture already supports this
- No major architectural changes needed

**3. Scalability**
- Can add multiple indigenous traditions
- Each tradition can have its own agent
- Community-controlled knowledge bases

**4. Authenticity**
- Indigenous knowledge agent speaks in its own voice
- Not diluted or mixed with other frameworks
- Respects cultural protocols

---

## Architecture Overview

### High-Level Flow

```
User Message
    ↓
OrchestratorAgent (coordinates)
    ↓
    ├──→ Personal Agent (Xavi)
    │    Framework: MN/AD/AQ
    │    Focus: Individual nature, personal goals
    │    Style: Socratic, warm, individual-focused
    │
    ├──→ Indigenous Knowledge Agent
    │    Framework: Indigenous Wisdom Traditions
    │    Focus: Community, relationships, land, balance
    │    Style: Storytelling, relationship-oriented, communal
    │
    └──→ Response Merger
         Combines both perspectives
         Presents unified or side-by-side view
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend UI                          │
│  - Chat interface with dual-agent indicators           │
│  - Toggle between unified/side-by-side views           │
│  - Agent attribution labels                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              API Layer (routes.py)                      │
│  - /api/xaviagent/chat (enhanced)                      │
│  - /api/xaviagent/indigenous-config                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           OrchestratorAgent (enhanced)                  │
│  - Detects org/user preference for indigenous agent    │
│  - Coordinates both agents                              │
│  - Merges responses                                     │
└─────────────────────────────────────────────────────────┘
         ↓                    ↓
┌─────────────────┐  ┌──────────────────────────┐
│  Personal Agent  │  │ Indigenous Knowledge     │
│  (Xavi)          │  │ Agent                     │
│                  │  │                          │
│  - ScoringAgent  │  │ - IndigenousEngine       │
│  - Conversational│  │ - Knowledge RAG          │
│  - Validator     │  │ - Cultural Protocols     │
└─────────────────┘  └──────────────────────────┘
```

---

## Cultural Considerations

### Critical Requirements

**1. Indigenous Oversight & Governance**
- **Knowledge Keeper Review:** All content must be reviewed by indigenous knowledge keepers
- **Approval Process:** Content approval workflow before going live
- **Ongoing Relationship:** Regular check-ins with indigenous advisors
- **Community Control:** Indigenous communities control what knowledge is shared

**2. Attribution & Respect**
- **Clear Attribution:** Every piece of knowledge attributed to specific tradition
- **No Generic "Indigenous":** Must specify which tradition (Hawaiian, Lakota, etc.)
- **Intellectual Property:** Respect for indigenous IP rights
- **Sacred Knowledge:** Protocols for what cannot be shared

**3. Community Benefit**
- **Revenue Sharing:** If commercial, revenue flows back to communities
- **Community Input:** Regular feedback loops with indigenous partners
- **Capacity Building:** Support indigenous communities in using the platform
- **Reciprocal Relationship:** Not extractive, but mutually beneficial

**4. Cultural Protocols**
- **Seasonal Knowledge:** Some knowledge only shared in certain seasons
- **Context Requirements:** Some knowledge requires specific contexts
- **Elder Approval:** Some knowledge requires elder approval
- **Ceremonial Respect:** Honor ceremonial aspects of knowledge

### Implementation Principles

1. **Nothing goes live without indigenous approval**
2. **Indigenous communities control their knowledge**
3. **Ongoing relationship, not one-time integration**
4. **Respect for protocols and sacred knowledge**
5. **Community benefit is built into the model**

---

## Technical Implementation

### Phase 1: Foundation Components

#### 1.1 Indigenous Knowledge Framework Engine

**File:** `backend/api/xaviagent/frameworks/indigenous_engine.py`

```python
"""
Indigenous Knowledge Framework Engine

Interprets user messages through indigenous wisdom traditions.
Focuses on: community, relationships, land, balance, reciprocity.
"""

from typing import Dict, List, Optional, Any
from ..base import FrameworkEngine, FrameworkInputV1, FrameworkOutputV1
from ..models import MomentState
import logging

logger = logging.getLogger(__name__)


class IndigenousKnowledgeEngine(FrameworkEngine):
    """
    Framework Engine that interprets through indigenous wisdom traditions.
    
    Knowledge Sources:
    - Hawaiian: Pono, 'Ohana, 'Āina, Kuleana
    - Other traditions (as approved by knowledge keepers)
    
    Design Principles:
    1. Community-oriented (not individual-focused)
    2. Relationship-centered (connections matter more than achievements)
    3. Land-aware (connection to place and environment)
    4. Balance-focused (harmony, not optimization)
    5. Storytelling-based (narrative over analysis)
    """
    
    def __init__(self, tradition: str = "Hawaiian"):
        """
        Initialize with specific indigenous tradition.
        
        Args:
            tradition: Which tradition to use (Hawaiian, Lakota, etc.)
        """
        super().__init__(
            engine_id=f"indigenous_{tradition.lower()}",
            engine_name=f"{tradition} Wisdom Engine",
            version="1.0.0"
        )
        self.tradition = tradition
        self.knowledge_base = self._load_knowledge_base(tradition)
    
    def _load_knowledge_base(self, tradition: str) -> Dict:
        """Load curated knowledge base for tradition."""
        # Query indigenous_knowledge_sources table
        # Filter by tradition, approved status
        # Return structured knowledge
        pass
    
    async def infer_state(
        self, 
        input_data: FrameworkInputV1
    ) -> Optional[Dict[str, Any]]:
        """
        Interpret user message through indigenous lens.
        
        Focus areas:
        - Community relationships (who is this person connected to?)
        - Land/environment connection (where are they? what's their place?)
        - Balance (is there harmony or imbalance?)
        - Responsibility (what is their kuleana/duty?)
        - Reciprocity (what are they giving and receiving?)
        """
        user_message = input_data.user_message
        conversation_history = input_data.conversation_context
        
        # Use RAG to find relevant indigenous wisdom
        relevant_wisdom = await self._retrieve_wisdom(user_message)
        
        # Interpret through indigenous framework
        interpretation = {
            "community_connections": self._analyze_relationships(user_message),
            "land_connection": self._analyze_place(user_message),
            "balance_state": self._analyze_balance(user_message),
            "responsibility": self._identify_kuleana(user_message),
            "reciprocity": self._analyze_reciprocity(user_message)
        }
        
        return interpretation
    
    async def generate_guidance(
        self,
        state: Dict[str, Any],
        input_data: FrameworkInputV1
    ) -> FrameworkOutputV1:
        """
        Generate guidance rooted in indigenous wisdom.
        
        Style:
        - Storytelling and metaphor
        - Relationship-oriented
        - Community-focused
        - Land-aware
        - Balance-seeking
        """
        # Build guidance using indigenous wisdom
        guidance = self._craft_indigenous_guidance(state, input_data)
        
        return FrameworkOutputV1(
            engine_id=self.engine_id,
            version=self.version,
            interpretation={
                "mirror": guidance["mirror"],  # Reflects community/relationship perspective
                "reframe": guidance["reframe"],  # Reframes through indigenous lens
                "key_tensions": guidance["tensions"],  # Community/individual tensions
                "latent_needs": guidance["needs"]  # What community/land needs
            },
            options=guidance["options"],  # Community-oriented options
            smallest_move=guidance["smallest_move"],  # Relationship-building move
            mastery_hooks=guidance["mastery_hooks"],  # Community practice hooks
            safety_meta={
                "tone_mode": "grounding",  # Indigenous wisdom is grounding
                "escalation_needed": False
            }
        )
    
    async def _retrieve_wisdom(self, user_message: str) -> List[Dict]:
        """Retrieve relevant indigenous wisdom from RAG knowledge base."""
        # Query indigenous_knowledge_sources via RAG
        # Filter by: tradition, topic, cultural protocol
        # Return approved wisdom snippets
        pass
    
    def _analyze_relationships(self, message: str) -> Dict:
        """Analyze community/relationship aspects of message."""
        # Look for: family, community, connections, isolation
        pass
    
    def _analyze_place(self, message: str) -> Dict:
        """Analyze land/environment connection in message."""
        # Look for: location, environment, connection to place
        pass
    
    def _analyze_balance(self, message: str) -> Dict:
        """Analyze balance/harmony state."""
        # Look for: imbalance, harmony, tension, flow
        pass
    
    def _identify_kuleana(self, message: str) -> Dict:
        """Identify responsibility/duty (kuleana in Hawaiian)."""
        # Look for: responsibilities, duties, what they're called to do
        pass
    
    def _analyze_reciprocity(self, message: str) -> Dict:
        """Analyze giving/receiving balance."""
        # Look for: what they give, what they receive, balance
        pass
    
    def _craft_indigenous_guidance(
        self, 
        state: Dict, 
        input_data: FrameworkInputV1
    ) -> Dict:
        """Craft guidance using indigenous wisdom and storytelling."""
        # Use retrieved wisdom
        # Apply cultural protocols
        # Craft response in indigenous style
        pass
```

#### 1.2 Indigenous Knowledge Agent

**File:** `backend/api/xaviagent/agents/indigenous_agent.py`

```python
"""
Indigenous Knowledge Agent

Conversational agent that brings indigenous wisdom to conversations.
Works alongside Personal Agent (Xavi) to provide dual perspectives.
"""

from typing import Dict, List, Optional, Any
from .base import BaseAgent, AgentRequest, AgentResponse
from ..frameworks.indigenous_engine import IndigenousKnowledgeEngine
import logging

logger = logging.getLogger(__name__)


class IndigenousKnowledgeAgent(BaseAgent):
    """
    Agent that provides indigenous wisdom perspective.
    
    Role:
    - Bring community/relationship perspective
    - Share relevant indigenous wisdom
    - Offer balance and harmony guidance
    - Connect to land and place
    
    Personality:
    - Wise, grounded, relationship-oriented
    - Storytelling style
    - Community-focused
    - Respectful of individual journey
    """
    
    def __init__(self, tradition: str = "Hawaiian"):
        super().__init__(
            agent_name="indigenous_knowledge",
            version="1.0.0"
        )
        self.tradition = tradition
        self.framework_engine = IndigenousKnowledgeEngine(tradition=tradition)
        self.personality = self._load_personality(tradition)
    
    def _load_personality(self, tradition: str) -> Dict:
        """Load personality traits for tradition."""
        personalities = {
            "Hawaiian": {
                "tone": "warm, grounded, community-oriented",
                "style": "storytelling, relationship-focused",
                "values": ["pono", "ohana", "kuleana", "aloha"],
                "metaphors": ["ocean", "mountain", "plant growth", "seasons"]
            }
        }
        return personalities.get(tradition, personalities["Hawaiian"])
    
    async def _execute_internal(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Generate indigenous wisdom perspective on user's message.
        
        Process:
        1. Interpret through indigenous framework
        2. Retrieve relevant wisdom
        3. Craft response in indigenous style
        4. Ensure cultural protocol compliance
        """
        user_message = request.conversation_history[-1].get("content", "")
        context = request.conversation_history
        
        # Convert to FrameworkInputV1 format
        framework_input = self._convert_to_framework_input(request)
        
        # Get indigenous interpretation
        state = await self.framework_engine.infer_state(framework_input)
        
        # Generate guidance
        guidance = await self.framework_engine.generate_guidance(
            state, 
            framework_input
        )
        
        # Craft conversational response
        response_text = self._craft_response(guidance, context)
        
        return {
            "message": response_text,
            "perspective": "indigenous_wisdom",
            "tradition": self.tradition,
            "reasoning": guidance.interpretation.get("reframe", ""),
            "framework_state": state
        }
    
    def _convert_to_framework_input(self, request: AgentRequest) -> FrameworkInputV1:
        """Convert AgentRequest to FrameworkInputV1."""
        # Map request fields to framework input
        pass
    
    def _craft_response(
        self, 
        guidance: FrameworkOutputV1, 
        context: List[Dict]
    ) -> str:
        """
        Craft conversational response in indigenous style.
        
        Style elements:
        - Storytelling/metaphor
        - Relationship language
        - Community perspective
        - Balance and harmony focus
        """
        # Use guidance to craft natural language response
        # Apply personality traits
        # Ensure cultural protocol compliance
        pass
```

#### 1.3 Enhanced Orchestrator

**File:** `backend/api/xaviagent/agents/orchestrator.py` (modifications)

```python
# Add to OrchestratorAgent class

def __init__(self):
    # ... existing code ...
    self.indigenous_agent: Optional[BaseAgent] = None

def set_indigenous_agent(self, agent: BaseAgent):
    """Wire up indigenous knowledge agent."""
    self.indigenous_agent = agent
    self.logger.info("✅ Indigenous knowledge agent connected")

async def _execute_internal(self, request: AgentRequest) -> Dict[str, Any]:
    """
    Enhanced orchestration with indigenous agent support.
    """
    # ... existing code ...
    
    # Check if indigenous agent should be involved
    should_use_indigenous = self._should_use_indigenous_agent(request)
    
    if should_use_indigenous and self.indigenous_agent:
        # Get both perspectives
        personal_response = await self._get_personal_response(request)
        indigenous_response = await self.indigenous_agent.execute(request)
        
        # Merge responses
        merged_response = self._merge_agent_responses(
            personal_response,
            indigenous_response
        )
        
        return merged_response
    else:
        # Standard flow (personal agent only)
        return await self._get_personal_response(request)

def _should_use_indigenous_agent(self, request: AgentRequest) -> bool:
    """Determine if indigenous agent should participate."""
    # Check org setting (The Four Cups = always on)
    org_id = request.metadata.get("org_id")
    if org_id == FOUR_CUPS_ORG_ID:
        return True
    
    # Check user preference
    user_preference = request.metadata.get("indigenous_agent_enabled")
    if user_preference is True:
        return True
    
    # Check session setting
    session_setting = request.metadata.get("session_indigenous_enabled")
    if session_setting is True:
        return True
    
    return False

def _merge_agent_responses(
    self,
    personal: Dict,
    indigenous: Dict
) -> Dict:
    """
    Merge responses from both agents.
    
    Options:
    1. Unified response (both perspectives woven together)
    2. Side-by-side (both perspectives shown separately)
    3. Toggle (user can switch views)
    """
    merge_mode = self._get_merge_mode()
    
    if merge_mode == "unified":
        return self._create_unified_response(personal, indigenous)
    elif merge_mode == "side_by_side":
        return self._create_side_by_side_response(personal, indigenous)
    else:
        # Default: unified
        return self._create_unified_response(personal, indigenous)

def _create_unified_response(
    self,
    personal: Dict,
    indigenous: Dict
) -> Dict:
    """Create single response weaving both perspectives."""
    # Combine insights from both agents
    # Maintain both voices but in one flow
    # Example:
    # "I notice [personal insight]. And from another perspective, 
    # [indigenous wisdom]. Together, this suggests [merged insight]."
    pass

def _create_side_by_side_response(
    self,
    personal: Dict,
    indigenous: Dict
) -> Dict:
    """Create response showing both perspectives separately."""
    return {
        "message": None,  # No unified message
        "perspectives": {
            "personal": {
                "agent": "Xavi",
                "message": personal.get("message"),
                "reasoning": personal.get("reasoning")
            },
            "indigenous": {
                "agent": f"{indigenous.get('tradition', 'Indigenous')} Wisdom",
                "message": indigenous.get("message"),
                "reasoning": indigenous.get("reasoning")
            }
        },
        "current_scores": personal.get("current_scores", {}),
        "is_complete": personal.get("is_complete", False)
    }
```

---

## Database Schema

### New Tables

#### 1. Indigenous Knowledge Sources

```sql
CREATE TABLE xaviagent.indigenous_knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tradition identification
    tradition VARCHAR(100) NOT NULL,  -- "Hawaiian", "Lakota", etc.
    tradition_variant VARCHAR(100),  -- Specific lineage/region if applicable
    
    -- Content
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,  -- The wisdom/knowledge itself
    summary TEXT,  -- Brief summary for search
    
    -- Cultural protocols
    cultural_protocols JSONB,  -- {
        --   "seasonal": true/false,
        --   "context_required": ["ceremony", "elder_present"],
        --   "sacred_level": "public" | "community" | "ceremonial",
        --   "attribution_required": true/false
    -- }
    
    -- Attribution
    knowledge_keeper_id UUID REFERENCES core.users(id),  -- Who approved this
    knowledge_keeper_name VARCHAR(200),  -- Name for attribution
    source_reference TEXT,  -- Original source (book, oral tradition, etc.)
    
    -- Approval & governance
    approval_status VARCHAR(50) DEFAULT 'pending',  -- pending, approved, rejected
    approved_by UUID REFERENCES core.users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- Metadata
    tags TEXT[],  -- Topics, themes
    keywords TEXT[],  -- For search
    language VARCHAR(10) DEFAULT 'en',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES core.users(id)
);

-- Indexes
CREATE INDEX idx_indigenous_tradition ON xaviagent.indigenous_knowledge_sources(tradition);
CREATE INDEX idx_indigenous_approval ON xaviagent.indigenous_knowledge_sources(approval_status);
CREATE INDEX idx_indigenous_tags ON xaviagent.indigenous_knowledge_sources USING GIN(tags);
CREATE INDEX idx_indigenous_keywords ON xaviagent.indigenous_knowledge_sources USING GIN(keywords);

-- Full-text search
CREATE INDEX idx_indigenous_content_search ON xaviagent.indigenous_knowledge_sources 
    USING GIN(to_tsvector('english', content || ' ' || COALESCE(summary, '')));
```

#### 2. Indigenous Agent Configuration

```sql
CREATE TABLE xaviagent.indigenous_agent_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Scope (org-level or user-level)
    org_id UUID REFERENCES core.organizations(id),
    user_id UUID REFERENCES core.users(id),
    
    -- Configuration
    enabled BOOLEAN DEFAULT true,
    traditions TEXT[] DEFAULT ARRAY['Hawaiian'],  -- Which traditions to use
    merge_mode VARCHAR(50) DEFAULT 'unified',  -- unified, side_by_side, toggle
    
    -- Display preferences
    show_attribution BOOLEAN DEFAULT true,
    show_tradition_label BOOLEAN DEFAULT true,
    default_view VARCHAR(50) DEFAULT 'unified',  -- unified, personal_only, indigenous_only
    
    -- Cultural protocols
    respect_seasonal_knowledge BOOLEAN DEFAULT true,
    require_context BOOLEAN DEFAULT false,
    min_sacred_level VARCHAR(50) DEFAULT 'public',  -- public, community, ceremonial
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT scope_check CHECK (
        (org_id IS NOT NULL AND user_id IS NULL) OR
        (org_id IS NULL AND user_id IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_indigenous_config_org ON xaviagent.indigenous_agent_config(org_id);
CREATE INDEX idx_indigenous_config_user ON xaviagent.indigenous_agent_config(user_id);
```

#### 3. Knowledge Keeper Registry

```sql
CREATE TABLE xaviagent.indigenous_knowledge_keepers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES core.users(id) UNIQUE,
    
    -- Identity
    name VARCHAR(200) NOT NULL,
    tradition VARCHAR(100) NOT NULL,
    role VARCHAR(100),  -- "Elder", "Knowledge Keeper", "Cultural Advisor", etc.
    
    -- Authority
    approval_level VARCHAR(50) DEFAULT 'reviewer',  -- reviewer, approver, elder
    can_approve BOOLEAN DEFAULT false,
    can_reject BOOLEAN DEFAULT false,
    
    -- Contact & relationship
    contact_email VARCHAR(255),
    relationship_notes TEXT,  -- How we work together
    
    -- Status
    active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_knowledge_keepers_tradition ON xaviagent.indigenous_knowledge_keepers(tradition);
CREATE INDEX idx_knowledge_keepers_active ON xaviagent.indigenous_knowledge_keepers(active);
```

#### 4. Usage Tracking

```sql
CREATE TABLE xaviagent.indigenous_agent_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Session tracking
    session_id UUID NOT NULL,
    user_id UUID REFERENCES core.users(id),
    org_id UUID REFERENCES core.organizations(id),
    
    -- What was used
    tradition VARCHAR(100) NOT NULL,
    knowledge_source_id UUID REFERENCES xaviagent.indigenous_knowledge_sources(id),
    
    -- Context
    user_message TEXT,
    agent_response TEXT,
    merge_mode VARCHAR(50),
    
    -- Feedback
    user_feedback VARCHAR(50),  -- helpful, not_helpful, inappropriate
    feedback_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_indigenous_usage_session ON xaviagent.indigenous_agent_usage(session_id);
CREATE INDEX idx_indigenous_usage_user ON xaviagent.indigenous_agent_usage(user_id);
CREATE INDEX idx_indigenous_usage_tradition ON xaviagent.indigenous_agent_usage(tradition);
```

---

## API Design

### New Endpoints

#### 1. Indigenous Agent Configuration

```python
# GET /api/xaviagent/indigenous/config
# Get user/org configuration for indigenous agent

@router.get("/indigenous/config")
async def get_indigenous_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get indigenous agent configuration for user or org.
    
    Returns:
    {
        "enabled": true,
        "traditions": ["Hawaiian"],
        "merge_mode": "unified",
        "show_attribution": true,
        "default_view": "unified"
    }
    """
    pass

# PUT /api/xaviagent/indigenous/config
# Update configuration

@router.put("/indigenous/config")
async def update_indigenous_config(
    config: IndigenousAgentConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update indigenous agent configuration."""
    pass
```

#### 2. Knowledge Management (Admin/Knowledge Keeper Only)

```python
# POST /api/xaviagent/indigenous/knowledge
# Add new knowledge (requires knowledge keeper approval)

@router.post("/indigenous/knowledge")
async def create_knowledge_source(
    knowledge: IndigenousKnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new indigenous knowledge source.
    Requires knowledge keeper role.
    Starts in 'pending' approval status.
    """
    pass

# GET /api/xaviagent/indigenous/knowledge
# List knowledge sources (filtered by approval status)

@router.get("/indigenous/knowledge")
async def list_knowledge_sources(
    tradition: Optional[str] = None,
    approval_status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List indigenous knowledge sources."""
    pass

# PUT /api/xaviagent/indigenous/knowledge/{id}/approve
# Approve knowledge source (knowledge keeper only)

@router.put("/indigenous/knowledge/{id}/approve")
async def approve_knowledge_source(
    knowledge_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve knowledge source for use."""
    pass
```

#### 3. Enhanced Chat Endpoint

```python
# POST /api/xaviagent/chat (enhanced)
# Now supports indigenous agent

@router.post("/chat")
async def chat_with_agents(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat endpoint enhanced to support indigenous agent.
    
    Request can include:
    {
        "message": "user message",
        "session_id": "...",
        "indigenous_enabled": true,  # Override config
        "merge_mode": "unified"  # Override config
    }
    
    Response includes:
    {
        "message": "...",  # Unified or personal-only
        "perspectives": {  # If side-by-side mode
            "personal": {...},
            "indigenous": {...}
        },
        "attribution": {
            "tradition": "Hawaiian",
            "knowledge_keeper": "Name"
        }
    }
    """
    pass
```

---

## Frontend Integration

### UI Components

#### 1. Agent Indicator

```typescript
// components/chat/AgentIndicator.tsx
interface AgentIndicatorProps {
  agents: Array<{
    name: string;
    type: 'personal' | 'indigenous';
    tradition?: string;
  }>;
  mergeMode: 'unified' | 'side_by_side' | 'toggle';
}

const AgentIndicator: React.FC<AgentIndicatorProps> = ({ agents, mergeMode }) => {
  return (
    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
      {agents.map(agent => (
        <Chip
          key={agent.name}
          label={agent.name}
          icon={agent.type === 'indigenous' ? <NatureIcon /> : <PersonIcon />}
          color={agent.type === 'indigenous' ? 'primary' : 'default'}
          size="small"
        />
      ))}
    </Box>
  );
};
```

#### 2. Dual Perspective View

```typescript
// components/chat/DualPerspectiveView.tsx
interface DualPerspectiveViewProps {
  personal: {
    message: string;
    agent: string;
    reasoning?: string;
  };
  indigenous: {
    message: string;
    agent: string;
    tradition: string;
    reasoning?: string;
    attribution?: string;
  };
  mergeMode: 'unified' | 'side_by_side';
}

const DualPerspectiveView: React.FC<DualPerspectiveViewProps> = ({
  personal,
  indigenous,
  mergeMode
}) => {
  if (mergeMode === 'unified') {
    return (
      <Box>
        <Typography variant="body1">{personal.message}</Typography>
        <Box sx={{ mt: 1, pl: 2, borderLeft: '2px solid', borderColor: 'primary.main' }}>
          <Typography variant="body2" color="text.secondary">
            <strong>{indigenous.agent}:</strong> {indigenous.message}
          </Typography>
          {indigenous.attribution && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              Wisdom from {indigenous.tradition} tradition
            </Typography>
          )}
        </Box>
      </Box>
    );
  }
  
  // Side-by-side view
  return (
    <Grid container spacing={2}>
      <Grid item xs={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle2">{personal.agent}</Typography>
          <Typography variant="body1">{personal.message}</Typography>
        </Paper>
      </Grid>
      <Grid item xs={6}>
        <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
          <Typography variant="subtitle2">
            {indigenous.agent}
            {indigenous.attribution && (
              <Chip label={indigenous.tradition} size="small" sx={{ ml: 1 }} />
            )}
          </Typography>
          <Typography variant="body1">{indigenous.message}</Typography>
        </Paper>
      </Grid>
    </Grid>
  );
};
```

#### 3. Configuration UI

```typescript
// pages/settings/IndigenousAgentSettings.tsx
const IndigenousAgentSettings: React.FC = () => {
  const [config, setConfig] = useState<IndigenousAgentConfig>({
    enabled: true,
    traditions: ['Hawaiian'],
    mergeMode: 'unified',
    showAttribution: true
  });
  
  return (
    <Box>
      <Typography variant="h6">Indigenous Knowledge Agent</Typography>
      
      <FormControlLabel
        control={
          <Switch
            checked={config.enabled}
            onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
          />
        }
        label="Enable Indigenous Knowledge Agent"
      />
      
      <FormControl fullWidth sx={{ mt: 2 }}>
        <InputLabel>Merge Mode</InputLabel>
        <Select
          value={config.mergeMode}
          onChange={(e) => setConfig({ ...config, mergeMode: e.target.value })}
        >
          <MenuItem value="unified">Unified Response</MenuItem>
          <MenuItem value="side_by_side">Side by Side</MenuItem>
          <MenuItem value="toggle">Toggle View</MenuItem>
        </Select>
      </FormControl>
      
      <FormControlLabel
        control={
          <Switch
            checked={config.showAttribution}
            onChange={(e) => setConfig({ ...config, showAttribution: e.target.checked })}
          />
        }
        label="Show Attribution"
        sx={{ mt: 2 }}
      />
    </Box>
  );
};
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-3)

**Goal:** Build core infrastructure

**Tasks:**
1. ✅ Create database schema
2. ✅ Build `IndigenousKnowledgeEngine` framework
3. ✅ Build `IndigenousKnowledgeAgent`
4. ✅ Enhance `OrchestratorAgent` for multi-agent coordination
5. ✅ Create knowledge management API endpoints
6. ✅ Set up RAG for indigenous knowledge

**Deliverables:**
- Database tables created and migrated
- Framework engine functional
- Agent can respond (with placeholder knowledge)
- Orchestrator coordinates both agents
- Basic API endpoints working

**Success Criteria:**
- Both agents can be invoked
- Responses are generated (even if placeholder)
- Database schema supports knowledge management

---

### Phase 2: Knowledge Curation (Weeks 4-6)

**Goal:** Curate and load indigenous knowledge

**Tasks:**
1. Work with The Four Cups to identify knowledge sources
2. Work with indigenous knowledge keepers to curate content
3. Build knowledge approval workflow
4. Load initial Hawaiian knowledge base
5. Set up attribution system
6. Test cultural protocol compliance

**Deliverables:**
- Curated knowledge base (Hawaiian tradition)
- Approval workflow functional
- Knowledge keepers can review/approve
- Attribution system working

**Success Criteria:**
- Knowledge base has 50+ approved entries
- Approval workflow tested
- Knowledge keepers can use the system

---

### Phase 3: Integration & Testing (Weeks 7-9)

**Goal:** Integrate with frontend and test

**Tasks:**
1. Build frontend components
2. Integrate with chat interface
3. Add configuration UI
4. Test with The Four Cups users
5. Gather feedback
6. Refine responses and merging logic

**Deliverables:**
- Frontend shows dual perspectives
- Configuration UI functional
- Test users can use the system
- Feedback collected and analyzed

**Success Criteria:**
- Users can see both agent perspectives
- Configuration works
- Test users provide positive feedback
- No major bugs

---

### Phase 4: Refinement & Launch (Weeks 10-12)

**Goal:** Polish and launch

**Tasks:**
1. Refine agent responses based on feedback
2. Improve merging logic
3. Add more knowledge sources
4. Performance optimization
5. Documentation
6. Launch to The Four Cups

**Deliverables:**
- Polished user experience
- Expanded knowledge base
- Performance optimized
- Documentation complete
- Live for The Four Cups users

**Success Criteria:**
- Users report high satisfaction
- Response quality is high
- Performance is acceptable
- Knowledge base is comprehensive

---

## Testing Strategy

### Unit Tests

```python
# tests/xaviagent/test_indigenous_engine.py

def test_indigenous_engine_initialization():
    """Test engine initializes correctly."""
    engine = IndigenousKnowledgeEngine(tradition="Hawaiian")
    assert engine.tradition == "Hawaiian"
    assert engine.engine_id == "indigenous_hawaiian"

def test_indigenous_engine_state_inference():
    """Test state inference through indigenous lens."""
    engine = IndigenousKnowledgeEngine(tradition="Hawaiian")
    input_data = FrameworkInputV1(...)
    state = await engine.infer_state(input_data)
    assert "community_connections" in state
    assert "balance_state" in state

def test_cultural_protocol_compliance():
    """Test that cultural protocols are respected."""
    # Test seasonal knowledge
    # Test context requirements
    # Test sacred level restrictions
    pass
```

### Integration Tests

```python
# tests/xaviagent/test_indigenous_integration.py

async def test_dual_agent_conversation():
    """Test both agents respond in conversation."""
    orchestrator = OrchestratorAgent()
    orchestrator.set_scoring_agent(scoring_agent)
    orchestrator.set_conversational_agent(conversational_agent)
    orchestrator.set_indigenous_agent(indigenous_agent)
    
    request = AgentRequest(...)
    response = await orchestrator.execute(request)
    
    assert "perspectives" in response or "message" in response
    assert response.get("indigenous_participated") == True

async def test_knowledge_approval_workflow():
    """Test knowledge approval process."""
    # Create knowledge source
    # Submit for approval
    # Knowledge keeper approves
    # Verify it's available for use
    pass
```

### User Acceptance Testing

**Test Scenarios:**
1. User enables indigenous agent → sees both perspectives
2. User disables indigenous agent → sees only personal agent
3. User switches merge modes → view changes appropriately
4. Knowledge keeper approves content → appears in responses
5. Cultural protocol blocks content → appropriate message shown

---

## Rollout Plan

### Stage 1: Internal Testing (Week 9)
- Test with Xavigate team
- Verify all functionality
- Fix critical bugs

### Stage 2: The Four Cups Beta (Week 10)
- Deploy to The Four Cups org
- 5-10 beta testers
- Collect feedback
- Daily check-ins

### Stage 3: The Four Cups Full (Week 11-12)
- Roll out to all Four Cups users
- Monitor usage and feedback
- Support and iterate

### Stage 4: Documentation & Expansion (Week 13+)
- Document for other orgs
- Plan expansion to other traditions
- Build community of knowledge keepers

---

## Success Metrics

### User Engagement
- **Adoption Rate:** % of Four Cups users who enable indigenous agent
- **Usage Frequency:** How often indigenous agent is invoked
- **Session Length:** Do conversations with indigenous agent last longer?
- **Return Rate:** Do users return more when indigenous agent is enabled?

### Quality Metrics
- **User Satisfaction:** Survey scores (1-5 scale)
- **Helpfulness:** "Was this helpful?" feedback
- **Cultural Appropriateness:** Knowledge keeper reviews
- **Response Quality:** Human evaluation of responses

### Technical Metrics
- **Response Time:** Latency for dual-agent responses
- **Error Rate:** % of failed requests
- **Knowledge Base Coverage:** % of queries with relevant knowledge

### Cultural Metrics
- **Knowledge Keeper Satisfaction:** Are knowledge keepers happy?
- **Community Feedback:** What do indigenous communities say?
- **Attribution Accuracy:** Are attributions correct?
- **Protocol Compliance:** Are cultural protocols followed?

---

## Risk Mitigation

### Risk 1: Cultural Appropriation

**Mitigation:**
- Indigenous oversight required for all content
- Clear attribution to specific traditions
- Community control over knowledge
- Revenue sharing with communities
- Regular relationship check-ins

### Risk 2: Technical Complexity

**Mitigation:**
- Leverage existing multi-agent architecture
- Start simple (Hawaiian only)
- Iterate based on feedback
- Good test coverage

### Risk 3: Knowledge Quality

**Mitigation:**
- Approval workflow ensures quality
- Knowledge keepers review everything
- Ongoing refinement based on feedback
- Version control for knowledge sources

### Risk 4: User Confusion

**Mitigation:**
- Clear UI indicators
- Good onboarding
- Help documentation
- Support available

### Risk 5: Performance Issues

**Mitigation:**
- Caching for knowledge retrieval
- Async processing where possible
- Performance monitoring
- Load testing before launch

---

## Next Steps

### Immediate (This Week)
1. Review this plan with The Four Cups
2. Identify indigenous knowledge keepers to work with
3. Set up initial meeting with knowledge keepers
4. Create project timeline with The Four Cups

### Short Term (Next 2 Weeks)
1. Begin Phase 1 implementation
2. Set up database schema
3. Build framework engine skeleton
4. Start knowledge curation conversations

### Medium Term (Next Month)
1. Complete Phase 1
2. Begin knowledge curation
3. Build approval workflow
4. Start frontend integration

---

## Conclusion

This plan provides a comprehensive roadmap for integrating indigenous knowledge into XaviAgent as a collaborative agent. The approach honors indigenous wisdom traditions while leveraging existing technical architecture.

**Key Success Factors:**
1. Indigenous oversight and control
2. Cultural respect and protocols
3. Community benefit
4. Technical excellence
5. Ongoing relationship

**Expected Outcome:**
A system where users receive guidance from both their personal agent and indigenous wisdom traditions, creating richer, more holistic support that honors multiple ways of knowing.

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-XX  
**Status:** Ready for Review

