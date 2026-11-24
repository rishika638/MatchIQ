import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Conversation, Message, CandidateProfile, AgentAction, Opportunity, SavedOpportunity
from app.services.agent_tools import CareerAgentTools

logger = logging.getLogger(__name__)

GEMINI_TOOLS_DECLARATION = [
    {
        "name": "search_opportunities",
        "description": "Searches for job and career opportunities using hybrid semantic and keyword retrieval.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query terms or description"},
                "locations": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Optional location filters"},
                "work_modes": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "remote, hybrid, onsite"},
                "opportunity_types": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "full-time, contract, internship"},
                "min_salary": {"type": "INTEGER", "description": "Minimum annual compensation"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_opportunity_details",
        "description": "Fetches full details, compensation, description, and skills for a specific opportunity ID.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "opportunity_id": {"type": "STRING", "description": "The unique opportunity ID e.g. opp-seed-001"}
            },
            "required": ["opportunity_id"]
        }
    },
    {
        "name": "save_opportunity",
        "description": "Saves an opportunity into the candidate's personal tracker.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "opportunity_id": {"type": "STRING", "description": "The opportunity ID to save"},
                "notes": {"type": "STRING", "description": "Optional personal notes"}
            },
            "required": ["opportunity_id"]
        }
    },
    {
        "name": "compare_opportunities",
        "description": "Compares 2 to 4 opportunities side by side across skills, compensation, and compatibility.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "opportunity_ids": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "List of 2 to 4 opportunity IDs"}
            },
            "required": ["opportunity_ids"]
        }
    },
    {
        "name": "get_candidate_profile",
        "description": "Retrieves the current user's candidate profile, skills, and career preferences.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "update_candidate_preferences",
        "description": "Updates the candidate's job preferences (locations, work modes, salary).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "preferred_locations": {"type": "ARRAY", "items": {"type": "STRING"}},
                "preferred_work_modes": {"type": "ARRAY", "items": {"type": "STRING"}},
                "preferred_opportunity_types": {"type": "ARRAY", "items": {"type": "STRING"}},
                "preferred_min_salary": {"type": "INTEGER"}
            }
        }
    },
    {
        "name": "analyze_skill_gaps",
        "description": "Analyzes skill gaps and eligibility for an opportunity against the candidate's profile.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "opportunity_id": {"type": "STRING", "description": "The opportunity ID to analyze"}
            },
            "required": ["opportunity_id"]
        }
    }
]

class CareerAgentService:
    @classmethod
    def get_or_create_conversation(cls, db: Session, user_id: str, conversation_id: Optional[str] = None) -> Conversation:
        if conversation_id:
            convo = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            if convo:
                return convo

        new_convo = Conversation(
            user_id=user_id,
            title="Career Intelligence Strategy"
        )
        db.add(new_convo)
        db.commit()
        db.refresh(new_convo)
        return new_convo

    @classmethod
    def build_system_context(cls, db: Session, user_id: str) -> str:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        saved_opps = db.query(SavedOpportunity).filter(SavedOpportunity.user_id == user_id).all()
        saved_ids = [s.opportunity_id for s in saved_opps]

        profile_summary = "Candidate Profile: Not yet configured."
        if profile:
            profile_summary = (
                f"Candidate: {profile.headline or 'Candidate'}\n"
                f"Experience: {profile.experience_years} years\n"
                f"Skills: {', '.join(profile.skills or [])}\n"
                f"Preferred Work Modes: {profile.preferred_work_modes}\n"
                f"Preferred Locations: {profile.preferred_locations}\n"
                f"Preferred Opportunity Types: {profile.preferred_opportunity_types}\n"
                f"Preferred Min Salary: ${profile.preferred_min_salary:,}\n"
                f"Currently Saved Opportunities ({len(saved_ids)}): {', '.join(saved_ids[:5])}"
            )

        instructions = (
            "You are MatchIQ's AI Career Intelligence Copilot — an expert career strategist, "
            "technical talent analyst, and opportunity advisor. "
            "Always rely on actual tool execution results to answer questions about jobs, skills, "
            "and candidate alignment. Never invent fake jobs, companies, or salary numbers. "
            "Be transparent about matching heuristics and skill gaps."
        )

        return f"{instructions}\n\n=== USER CONTEXT ===\n{profile_summary}\n====================="

    @classmethod
    def execute_tool(cls, db: Session, user_id: str, conversation_id: str, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes real backend tools with Pydantic validation and audit logging in AgentAction.
        """
        tool_func = getattr(CareerAgentTools, tool_name, None)
        if not tool_func:
            return {"error": f"Tool '{tool_name}' is not recognized."}

        action = AgentAction(
            conversation_id=conversation_id,
            user_id=user_id,
            tool_name=tool_name,
            arguments=tool_args,
            execution_status="pending"
        )
        db.add(action)
        db.flush()

        try:
            result = tool_func(db=db, user_id=user_id, args=tool_args)
            action.result = result
            action.execution_status = "executed"
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            err_msg = f"Tool execution failed: {str(e)}"
            logger.error(err_msg)
            action.result = {"error": err_msg}
            action.execution_status = "failed"
            db.commit()
            return {"error": err_msg}

    @classmethod
    def _deterministic_agent_fallback(
        cls,
        db: Session,
        user_id: str,
        conversation_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Robust rule-based reasoning engine that extracts intent and triggers real tool execution
        when LLM credentials are not available or during network isolation.
        """
        msg_lower = user_message.lower()
        tools_executed = []

        # 1. Check for specific Opportunity ID mention (e.g. opp-seed-002)
        opp_id_match = re.search(r'(opp-[a-z0-9-]+)', msg_lower)
        target_opp_id = opp_id_match.group(1) if opp_id_match else None

        # Compare opportunities
        opp_ids = list(dict.fromkeys(re.findall(r'(opp-[a-z0-9-]+)', msg_lower)))
        if len(opp_ids) >= 2 and any(k in msg_lower for k in ["compare", "versus", "side by side"]):
            tool_res = cls.execute_tool(db, user_id, conversation_id, "compare_opportunities", {"opportunity_ids": opp_ids[:4]})
            tools_executed.append({"name": "compare_opportunities", "args": {"opportunity_ids": opp_ids[:4]}, "result": tool_res})
            if "error" in tool_res:
                return {"response": tool_res["error"], "tools_executed": tools_executed}
            rows = []
            for opp in tool_res.get("opportunities", []):
                rows.append(
                    f"- **{opp['title']}** at **{opp['company']}** "
                    f"({opp['location']}, {opp['work_mode']}) — "
                    f"{opp.get('compatibility_score')}% match"
                )
            return {
                "response": "### Opportunity Comparison\n\n" + "\n".join(rows),
                "tools_executed": tools_executed
            }

        # 0. Intent: Update Candidate Preferences
        if any(k in msg_lower for k in ["update preferences", "change preference", "set preferred", "update my preference"]):
            args = {}
            if "remote" in msg_lower:
                args["preferred_work_modes"] = ["remote"]
            if "hybrid" in msg_lower:
                args["preferred_work_modes"] = ["hybrid"]
            if "onsite" in msg_lower or "on-site" in msg_lower:
                args["preferred_work_modes"] = ["onsite"]
            if "full-time" in msg_lower or "full time" in msg_lower:
                args["preferred_opportunity_types"] = ["full-time"]
            salary_match = re.search(r'\$?(\d{5,7})', msg_lower)
            if salary_match:
                args["preferred_min_salary"] = int(salary_match.group(1))
            if args:
                tool_res = cls.execute_tool(db, user_id, conversation_id, "update_candidate_preferences", args)
                tools_executed.append({"name": "update_candidate_preferences", "args": args, "result": tool_res})
                return {"response": tool_res.get("message", "Preference update processed."), "tools_executed": tools_executed}

        # 2. Intent: Skill Gap Analysis
        if target_opp_id and any(k in msg_lower for k in ["gap", "skill", "missing", "qualif", "compatib", "fit", "analyze"]):
            tool_res = cls.execute_tool(db, user_id, conversation_id, "analyze_skill_gaps", {"opportunity_id": target_opp_id})
            tools_executed.append({"name": "analyze_skill_gaps", "args": {"opportunity_id": target_opp_id}, "result": tool_res})
            
            if "error" in tool_res:
                response_text = f"I checked for skill gaps regarding opportunity `{target_opp_id}`, but encountered an issue: {tool_res['error']}"
            else:
                missing = ", ".join(tool_res["missing_required_skills"]) if tool_res["missing_required_skills"] else "None (Full match!)"
                matched = ", ".join(tool_res["matching_skills"][:5])
                response_text = (
                    f"### Skill Gap Analysis: {tool_res['opportunity_title']} at {tool_res['company']}\n\n"
                    f"- **Overall Compatibility:** {tool_res['overall_compatibility']}%\n"
                    f"- **Matching Competencies:** {matched}\n"
                    f"- **Missing Required Skills:** {missing}\n\n"
                    f"**Preparation Suggestions:**\n" + "\n".join(f"- {s}" for s in tool_res["preparation_suggestions"][:3])
                )
            return {"response": response_text, "tools_executed": tools_executed}

        # 3. Intent: Save Opportunity
        if target_opp_id and any(k in msg_lower for k in ["save", "bookmark", "track", "apply to"]):
            tool_res = cls.execute_tool(db, user_id, conversation_id, "save_opportunity", {"opportunity_id": target_opp_id})
            tools_executed.append({"name": "save_opportunity", "args": {"opportunity_id": target_opp_id}, "result": tool_res})
            return {"response": tool_res.get("message", "Processed save request."), "tools_executed": tools_executed}

        # 4. Intent: Opportunity Details
        if target_opp_id and any(k in msg_lower for k in ["detail", "info", "tell me about", "describe", "what is"]):
            tool_res = cls.execute_tool(db, user_id, conversation_id, "get_opportunity_details", {"opportunity_id": target_opp_id})
            tools_executed.append({"name": "get_opportunity_details", "args": {"opportunity_id": target_opp_id}, "result": tool_res})
            if "error" in tool_res:
                response_text = f"Could not retrieve details for `{target_opp_id}`: {tool_res['error']}"
            else:
                response_text = (
                    f"### {tool_res['title']} — {tool_res['company']}\n\n"
                    f"- **Location:** {tool_res['location']} ({tool_res['work_mode']})\n"
                    f"- **Compensation:** {tool_res['compensation']}\n"
                    f"- **Tenure Requirement:** {tool_res['experience_range']}\n"
                    f"- **Required Skills:** {', '.join(tool_res['required_skills'])}\n\n"
                    f"{tool_res['description'][:280]}..."
                )
            return {"response": response_text, "tools_executed": tools_executed}

        # 5. Intent: Profile / Preferences
        if any(k in msg_lower for k in ["my profile", "my skills", "what are my preferences", "view profile"]):
            tool_res = cls.execute_tool(db, user_id, conversation_id, "get_candidate_profile", {})
            tools_executed.append({"name": "get_candidate_profile", "args": {}, "result": tool_res})
            if "error" in tool_res:
                response_text = f"Unable to fetch profile: {tool_res['error']}"
            else:
                response_text = (
                    f"### Candidate Profile Overview\n\n"
                    f"- **Headline:** {tool_res.get('headline')}\n"
                    f"- **Experience:** {tool_res.get('experience_years')} years\n"
                    f"- **Extracted Skills:** {', '.join(tool_res.get('skills', [])[:8])}\n"
                    f"- **Preferred Locations:** {', '.join(tool_res.get('preferred_locations', [])) or 'Any'}\n"
                    f"- **Target Modes:** {', '.join(tool_res.get('preferred_work_modes', [])) or 'Any'}\n"
                    f"- **Min Salary:** ${tool_res.get('preferred_min_salary', 0):,}"
                )
            return {"response": response_text, "tools_executed": tools_executed}

        # 6. Intent: Search / Opportunities Discovery (Default fallback)
        search_query = user_message
        for strip_phrase in ["search for", "find me", "look for", "show me", "jobs for", "opportunities involving"]:
            search_query = re.sub(strip_phrase, "", search_query, flags=re.IGNORECASE)
        search_query = search_query.strip(" ?.")
        if not search_query:
            search_query = "Software Engineer"

        tool_res = cls.execute_tool(db, user_id, conversation_id, "search_opportunities", {"query": search_query})
        tools_executed.append({"name": "search_opportunities", "args": {"query": search_query}, "result": tool_res})

        matches = tool_res.get("top_opportunities", [])
        if not matches:
            response_text = f"I ran a hybrid search for **'{search_query}'**, but didn't find exact active matches. Try broadening your query or updating location filters."
        else:
            list_md = []
            for m in matches[:4]:
                score_str = f" • **{m['compatibility_score']}% Match**" if m.get('compatibility_score') else ""
                list_md.append(f"- **{m['title']}** at **{m['company']}** ({m['location']}, {m['work_mode']}){score_str}\n  *Skills:* {', '.join(m['required_skills'][:4])}\n  *ID:* `{m['id']}`")

            response_text = (
                f"I executed a hybrid retrieval for **'{search_query}'** ({tool_res.get('total_matches', 0)} total candidates found). "
                f"Here are the top matches:\n\n" + "\n\n".join(list_md) +
                f"\n\n*Tip:* You can ask me to *'analyze skill gaps for {matches[0]['id']}'* or *'save {matches[0]['id']}'*."
            )
            if "then save" in msg_lower or "save the top" in msg_lower:
                top_id = matches[0]["id"]
                save_res = cls.execute_tool(db, user_id, conversation_id, "save_opportunity", {"opportunity_id": top_id})
                tools_executed.append({
                    "name": "save_opportunity",
                    "args": {"opportunity_id": top_id},
                    "result": save_res
                })
                response_text += f"\n\nI also saved the top result: `{top_id}`."

        return {"response": response_text, "tools_executed": tools_executed}

    @classmethod
    def chat(
        cls,
        db: Session,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Coordinates full conversation turn:
        1. Persists user message in database
        2. Tries Gemini with Google GenAI SDK tool calling if API key present
        3. Deterministic agent fallback if no key or API error
        4. Persists assistant message & executed tools in database
        """
        convo = cls.get_or_create_conversation(db, user_id, conversation_id)

        # 1. Record User Message
        user_msg_record = Message(
            conversation_id=convo.id,
            sender="user",
            content=message,
            metadata_json={"timestamp": datetime.now(timezone.utc).isoformat()}
        )
        db.add(user_msg_record)
        db.commit()

        # 2. Attempt Gemini generation if API key is provided
        gemini_success = False
        response_text = ""
        tools_executed = []

        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                system_instruction = cls.build_system_context(db, user_id)
                declarations = [
                    types.FunctionDeclaration(
                        name=item["name"],
                        description=item["description"],
                        parameters=item["parameters"]
                    )
                    for item in GEMINI_TOOLS_DECLARATION
                ]
                tool = types.Tool(function_declarations=declarations)
                contents = [message]

                for _ in range(5):
                    response = client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.3,
                            tools=[tool]
                        )
                    )
                    function_calls = []
                    for candidate in (response.candidates or []):
                        for part in (candidate.content.parts or []):
                            call = getattr(part, "function_call", None)
                            if call:
                                function_calls.append(call)
                    if not function_calls:
                        if response and response.text:
                            response_text = response.text
                            gemini_success = True
                        break

                    contents.append(response.candidates[0].content)
                    function_responses = []
                    for call in function_calls:
                        tool_name = call.name
                        tool_args = dict(call.args or {})
                        tool_res = cls.execute_tool(db, user_id, convo.id, tool_name, tool_args)
                        tools_executed.append({
                            "name": tool_name,
                            "args": tool_args,
                            "result": tool_res
                        })
                        function_responses.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=tool_res
                                )
                            )
                        )
                    contents.append(types.Content(role="tool", parts=function_responses))
                    continue
            except Exception as e:
                logger.warning(f"Gemini API invocation encountered error ({e}). Seamlessly engaging deterministic agent engine.")

        # 3. Fallback if Gemini was not active or produced no output
        if not gemini_success:
            fallback_res = cls._deterministic_agent_fallback(db, user_id, convo.id, message)
            response_text = fallback_res["response"]
            tools_executed = fallback_res["tools_executed"]

        # 4. Record Assistant Message in Database
        asst_msg_record = Message(
            conversation_id=convo.id,
            sender="assistant",
            content=response_text,
            tool_calls=[{"name": t["name"], "args": t["args"]} for t in tools_executed],
            tool_results=[{"name": t["name"], "result": t["result"]} for t in tools_executed],
            metadata_json={
                "model": settings.GEMINI_MODEL if gemini_success else "matchiq-deterministic-agent-v1",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        db.add(asst_msg_record)
        convo.updated_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "conversation_id": convo.id,
            "message_id": asst_msg_record.id,
            "response": response_text,
            "tools_executed": tools_executed,
            "model_used": settings.GEMINI_MODEL if gemini_success else "matchiq-deterministic-agent-v1"
        }

agent_service = CareerAgentService()
