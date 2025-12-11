# Specialist Task Handoff - Image Generation Implementation (RESTART)
**Generated:** 12-11-2025_0256
**Assigned To:** Image Generation Specialist
**Status:** Active (Restart)
**Original Handoff:** handoff_image_gen_12-11-2025.md

---

## 🔄 RESTART CONTEXT

This is a restart handoff. The original handoff was created earlier, and this document includes progress updates.

**Original Handoff:** See `handoff_image_gen_12-11-2025.md` for full original context.

**Conversation Summary:**
Completed API research. Found that Gemini Imagen requires different endpoint. Started implementation of generate_image() method. Modified ai_coordinator.py to add imports. Next steps: Complete the API call implementation and test in Discord.

---

## PROGRESS UPDATE

### Work Completed Since Last Handoff:
1. Completed API research. Found that Gemini Imagen requires different endpoint. Started implementation of generate_image() method. Modified ai_coordinator.py to add imports. Next steps: Complete the API call implementation and test in Discord.

### Work In Progress:
None

### Current Blockers:
None

### Important Discoveries:
None

### Files Modified:
None

### Next Immediate Steps:
None

### Context Summary:
Completed API research. Found that Gemini Imagen requires different endpoint. Started implementation of generate_image() method. Modified ai_coordinator.py to add imports. Next steps: Complete the API call implementation and test in Discord.

---

## ⚠️ CRITICAL SAFETY GUARDS

### Files You CAN Modify:
- `ai_coordinator.py` (only `generate_image()` method, lines 340-388)
  - You can modify the implementation inside this method
  - You can add helper methods if needed, but keep them in the AICoordinator class
  - You can update imports if needed for Gemini Imagen API

### Files You CANNOT Modify:
- `game_master/gm_commands.py` - Already calls image generation correctly (line 159)
- `game_master/gm_engine.py` - Key moment detection is working, don't touch
- `game_master/scene_images.py` - Framework is complete, just needs working backend
- `main.py` - Don't touch
- `config.py` - Don't modify existing config, but you can check if GOOGLE_API_KEY is available

### Dependencies:
None - can start immediately

### Testing Requirements:
1. Run `/nexus-test-list` and verify all tests still pass
2. Test manually in Discord:
   - Start a game: `/nexus-start mode: solo`
   - Trigger a key moment (combat, discovery, boss, etc.)
   - Verify image appears in the Discord embed
3. Verify no syntax errors: `python -m py_compile ai_coordinator.py`
4. Check logs for errors: Review `echo_bot.log` after testing

### Integration Points:
- `game_master/scene_images.py` line 59: Calls `await self.ai_coordinator.generate_image(prompt=prompt, user_id=user_id)`
- `game_master/gm_commands.py` line 159: Calls `await image_generator.generate_scene_image(...)` which then calls your method
- The method signature is: `async def generate_image(self, prompt: str, user_id: str) -> Optional[str]`
- Expected return: Image URL (string) or base64 data (string) or None if failed

### If Unsure:
**STOP and ask** - Don't assume, especially about:
- Changing the method signature (it's called from scene_images.py)
- Modifying other parts of ai_coordinator.py
- Adding new dependencies without checking requirements.txt

---



---

## TASK SPECIFIC CONTEXT

### Current State:
The `generate_image()` method exists in `ai_coordinator.py` (lines 340-388) but currently:
- Returns `None` (placeholder implementation)
- Has a TODO comment indicating Gemini Imagen API integration needed
- The framework in `scene_images.py` is complete and working
- Key moment detection in `gm_engine.py` is working
- The Discord integration in `gm_commands.py` is ready
- Everything is set up except the actual API call to generate images

### Target Implementation:
Implement Gemini Imagen API integration to actually generate images:
- Call Gemini Imagen API (or appropriate Google image generation API)
- Use the `prompt` parameter passed to the method
- Return the image URL or base64 data as a string
- Handle errors gracefully (return None, log errors)
- The method should work with the existing `GOOGLE_API_KEY` from config

### Technical Details:
- The method receives a prompt string that's already formatted for image generation
- The prompt includes scene description, moment type context, and character name if available
- You need to research Gemini Imagen API (or Google's image generation API)
- Check if `google.generativeai` already imported (it is, for text generation)
- May need to use a different Google API endpoint for images
- The `GOOGLE_API_KEY` is already configured in `config.py` and available as `Config.GOOGLE_API_KEY`
- Follow the same error handling pattern as other AI methods in the class (try/except, logging)

### Example Usage:
Once implemented, the flow will be:
1. Player triggers key moment in game (combat, discovery, etc.)
2. `gm_engine.py` detects key moment
3. `gm_commands.py` calls `image_generator.generate_scene_image()`
4. `scene_images.py` calls `ai_coordinator.generate_image(prompt, user_id)`
5. Your method calls Gemini Imagen API and returns image URL
6. Image appears in Discord embed

---



---

## REFERENCE DOCUMENTS

- **Master Context:** See `agent.md` for project standards, coding conventions, and world lore
- **Feature Documentation:** See `docs/AI_Game_Master_Feature_Doc.md` for Game Master feature details
- **Code Examples:**
  - `ai_coordinator.ask_mistral()` (lines 59-117) - Example async AI call pattern
  - `ai_coordinator.ask_gemini()` (lines 246-296) - Example Gemini API usage
  - `ai_coordinator.ask_claude()` (lines 122-177) - Example error handling pattern

---



---

## CODE PATTERNS TO FOLLOW

### Existing Patterns:
- Follow the async pattern in `ask_mistral()` and `ask_gemini()` methods
- Use the same error handling pattern: try/except with logging
- Check if client/model is available before using (like `ask_gemini()` does)
- Use `logger.info()`, `logger.error()`, `logger.warning()` for logging
- Return meaningful error messages or None on failure

### Coding Standards:
- Type hints required: The signature is already correct: `async def generate_image(self, prompt: str, user_id: str) -> Optional[str]:`
- Docstrings required: Update the existing docstring if needed
- Logging: Use `logger.info()`, `logger.error()` - never `print()`
- Error handling: Try/except with meaningful error messages, log errors
- Async/await: Method is already async, keep it that way

### File Organization:
- Keep implementation within the `generate_image()` method
- If you need helper methods, add them to the `AICoordinator` class
- Don't create new files unless absolutely necessary

---



---

## SAFETY CHECKLIST

Before making changes:
- [ ] Review this restart handoff and the original handoff
- [ ] Read `agent.md` for coding standards and world context
- [ ] Review existing code patterns in similar files
- [ ] Check if any other handoffs mention this file (use `handoff_manager.py check`)
- [ ] Understand the integration points
- [ ] Verify dependencies are met

Before committing:
- [ ] Run existing tests: `/nexus-test-list` → `/nexus-test-run` (if applicable)
- [ ] Test manually in Discord if applicable
- [ ] Verify no syntax errors: `python -m py_compile [your_file].py`
- [ ] Check logs for errors: Review `echo_bot.log`
- [ ] Verify integration points still work

---

## PROGRESS TRACKING

### Completed:
- [ ] Task analysis complete
- [ ] Implementation started
- [ ] Core functionality working
- [ ] Testing complete
- [ ] Integration verified

### Blockers:
None

### Notes:
[Any additional notes, discoveries, or important information]

---

## NEXT STEPS FOR SPECIALIST

1. Review this restart handoff and the original handoff (handoff_image_gen_12-11-2025.md)
2. Review all reference documents
3. Understand the progress made so far
4. Continue implementation from where we left off
5. Update this handoff with new progress
6. Mark as complete when done

---

**End of Restart Handoff**

*For the forgotten 99%, we rise.* 🔥
