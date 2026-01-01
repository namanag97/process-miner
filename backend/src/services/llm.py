"""LLM Integration Service - AI-Enhanced Process Mining.

Phase 5 PM4py Integration: Provides LLM capabilities for:
- Log abstraction for LLM context
- AI-powered queries and analysis
- Hypothesis generation
- Visualization explanation
"""

from typing import Any

import pm4py

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    LLM Integration Service for AI-Enhanced Process Mining.
    
    Supports OpenAI, Google (Gemini), and Anthropic (Claude) providers.
    Provides log abstractions suitable for LLM context windows.
    """

    # =========================================================================
    # Log Abstractions for LLM Context
    # =========================================================================

    def abstract_dfg(self, log) -> str:
        """
        Generate text abstraction of DFG for LLM context.
        
        Args:
            log: PM4Py event log (EventLog or DataFrame)
            
        Returns:
            Text description of the DFG
        """
        try:
            return pm4py.llm.abstract_dfg(log)
        except Exception as e:
            logger.error("abstract_dfg_failed", error=str(e))
            return f"Error abstracting DFG: {e}"

    def abstract_variants(self, log, max_variants: int = 10) -> str:
        """
        Generate text abstraction of process variants.
        
        Args:
            log: PM4Py event log
            max_variants: Maximum number of variants to include
            
        Returns:
            Text description of top variants
        """
        try:
            return pm4py.llm.abstract_variants(log, max_len=max_variants)
        except Exception as e:
            logger.error("abstract_variants_failed", error=str(e))
            return f"Error abstracting variants: {e}"

    def abstract_log_attributes(self, log) -> str:
        """
        Generate text summary of log attributes.
        
        Args:
            log: PM4Py event log
            
        Returns:
            Text description of available attributes
        """
        try:
            return pm4py.llm.abstract_log_attributes(log)
        except Exception as e:
            return f"Error abstracting attributes: {e}"

    def abstract_log_features(self, log) -> str:
        """
        Generate text summary of log features/statistics.
        
        Args:
            log: PM4Py event log
            
        Returns:
            Text description of log features
        """
        try:
            return pm4py.llm.abstract_log_features(log)
        except Exception as e:
            return f"Error abstracting features: {e}"

    def abstract_case(self, trace) -> str:
        """
        Generate text abstraction of a single case/trace.
        
        Args:
            trace: PM4Py Trace object
            
        Returns:
            Text description of the case
        """
        try:
            return pm4py.llm.abstract_case(trace)
        except Exception as e:
            return f"Error abstracting case: {e}"

    def abstract_petri_net(self, net, im, fm) -> str:
        """
        Generate text abstraction of a Petri net.
        
        Args:
            net: PetriNet object
            im: Initial marking
            fm: Final marking
            
        Returns:
            Text description of the Petri net structure
        """
        try:
            return pm4py.llm.abstract_petri_net(net, im, fm)
        except Exception as e:
            return f"Error abstracting Petri net: {e}"

    def abstract_declare(self, declare_model) -> str:
        """
        Generate text abstraction of DECLARE model.
        
        Args:
            declare_model: DECLARE model dictionary
            
        Returns:
            Text description of DECLARE constraints
        """
        try:
            return pm4py.llm.abstract_declare(declare_model)
        except Exception as e:
            return f"Error abstracting DECLARE: {e}"

    def abstract_log_skeleton(self, log_skeleton) -> str:
        """
        Generate text abstraction of Log Skeleton.
        
        Args:
            log_skeleton: Log skeleton model
            
        Returns:
            Text description of log skeleton constraints
        """
        try:
            return pm4py.llm.abstract_log_skeleton(log_skeleton)
        except Exception as e:
            return f"Error abstracting log skeleton: {e}"

    def abstract_temporal_profile(self, temporal_profile) -> str:
        """
        Generate text abstraction of Temporal Profile.
        
        Args:
            temporal_profile: Temporal profile dictionary
            
        Returns:
            Text description of temporal constraints
        """
        try:
            return pm4py.llm.abstract_temporal_profile(temporal_profile)
        except Exception as e:
            return f"Error abstracting temporal profile: {e}"

    # =========================================================================
    # OCEL Abstractions
    # =========================================================================

    def abstract_ocel(self, ocel) -> str:
        """
        Generate text abstraction of OCEL for LLM context.
        
        Args:
            ocel: PM4Py OCEL object
            
        Returns:
            Text description of the OCEL
        """
        try:
            return pm4py.llm.abstract_ocel(ocel)
        except Exception as e:
            return f"Error abstracting OCEL: {e}"

    def abstract_ocel_ocdfg(self, ocel) -> str:
        """
        Generate text abstraction of OCEL's OC-DFG.
        
        Args:
            ocel: PM4Py OCEL object
            
        Returns:
            Text description of the OC-DFG
        """
        try:
            return pm4py.llm.abstract_ocel_ocdfg(ocel)
        except Exception as e:
            return f"Error abstracting OC-DFG: {e}"

    # =========================================================================
    # AI Query Functions
    # =========================================================================

    async def openai_query(
        self, 
        prompt: str, 
        api_key: str,
        model: str = "gpt-4"
    ) -> str:
        """
        Send query to OpenAI API.
        
        Args:
            prompt: The prompt to send
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
            
        Returns:
            Model response as string
        """
        try:
            response = pm4py.llm.openai_query(prompt, api_key=api_key, openai_model=model)
            return response
        except Exception as e:
            logger.error("openai_query_failed", error=str(e))
            return f"Error: {e}"

    async def google_query(
        self, 
        prompt: str, 
        api_key: str,
        model: str = "gemini-1.5-pro"
    ) -> str:
        """
        Send query to Google Gemini API.
        
        Args:
            prompt: The prompt to send
            api_key: Google API key
            model: Model to use
            
        Returns:
            Model response as string
        """
        try:
            response = pm4py.llm.google_query(prompt, api_key=api_key, google_model=model)
            return response
        except Exception as e:
            logger.error("google_query_failed", error=str(e))
            return f"Error: {e}"

    async def anthropic_query(
        self, 
        prompt: str, 
        api_key: str,
        model: str = "claude-3-opus-20240229"
    ) -> str:
        """
        Send query to Anthropic Claude API.
        
        Args:
            prompt: The prompt to send
            api_key: Anthropic API key
            model: Model to use
            
        Returns:
            Model response as string
        """
        try:
            response = pm4py.llm.anthropic_query(prompt, api_key=api_key, anthropic_model=model)
            return response
        except Exception as e:
            logger.error("anthropic_query_failed", error=str(e))
            return f"Error: {e}"

    # =========================================================================
    # Advanced AI Analysis
    # =========================================================================

    async def analyze_log_with_ai(
        self,
        log,
        api_key: str,
        provider: str = "openai",
        analysis_type: str = "general"
    ) -> dict[str, Any]:
        """
        Perform AI-powered analysis of an event log.
        
        Args:
            log: PM4Py event log
            api_key: API key for the provider
            provider: "openai", "google", or "anthropic"
            analysis_type: Type of analysis ("general", "bottleneck", "compliance")
            
        Returns:
            Analysis results dictionary
        """
        # Create context from log
        context = self.abstract_dfg(log)
        context += "\n\n" + self.abstract_variants(log)
        context += "\n\n" + self.abstract_log_features(log)
        
        # Build analysis prompt
        if analysis_type == "bottleneck":
            prompt = f"""Given this process mining data:

{context}

Identify the top 3 bottlenecks in this process and suggest improvements."""
        elif analysis_type == "compliance":
            prompt = f"""Given this process mining data:

{context}

Identify potential compliance issues and deviations from expected process flow."""
        else:
            prompt = f"""Given this process mining data:

{context}

Provide a comprehensive analysis including:
1. Process overview
2. Key patterns
3. Potential issues
4. Improvement recommendations"""

        # Query appropriate provider
        if provider == "google":
            response = await self.google_query(prompt, api_key)
        elif provider == "anthropic":
            response = await self.anthropic_query(prompt, api_key)
        else:
            response = await self.openai_query(prompt, api_key)
        
        return {
            "analysis_type": analysis_type,
            "provider": provider,
            "response": response,
        }

    def automated_hypotheses(self, log) -> list[tuple]:
        """
        Generate automated hypotheses about the process from log.
        
        Uses PM4py's automated hypothesis formulation.
        
        Args:
            log: PM4Py event log
            
        Returns:
            List of hypothesis tuples
        """
        try:
            hypotheses = pm4py.llm.automated_hypothesis_formulation(log)
            return hypotheses
        except Exception as e:
            logger.error("automated_hypotheses_failed", error=str(e))
            return []


# Singleton instance
llm_service = LLMService()
