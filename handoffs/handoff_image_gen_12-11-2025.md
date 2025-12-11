# Specialist Task Handoff - Image Generation Implementation
**Generated:** 12-11-2025
**Assigned To:** Image Generation Specialist
**Status:** Active

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

## REFERENCE DOCUMENTS

- **Master Context:** See `agent.md` for project standards, coding conventions, and world lore
- **Feature Documentation:** See `docs/AI_Game_Master_Feature_Doc.md` for Game Master feature details
- **Code Examples:**
  - `ai_coordinator.ask_mistral()` (lines 59-117) - Example async AI call pattern
  - `ai_coordinator.ask_gemini()` (lines 246-296) - Example Gemini API usage
  - `ai_coordinator.ask_claude()` (lines 122-177) - Example error handling pattern

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

## SAFETY CHECKLIST

Before making changes:
- [x] Read `agent.md` for coding standards and world context
- [x] Review existing code patterns in similar files (ask_gemini, ask_mistral)
- [ ] Check if any other handoffs mention this file (use `handoff_manager.py check` when available)
- [x] Understand the integration points (scene_images.py line 59)
- [x] Verify dependencies are met (GOOGLE_API_KEY should be in .env)

Before committing:
- [ ] Run existing tests: `/nexus-test-list` → `/nexus-test-run` (if applicable)
- [ ] Test manually in Discord: `/nexus-start` → trigger key moment → verify image
- [ ] Verify no syntax errors: `python -m py_compile ai_coordinator.py`
- [ ] Check logs for errors: Review `echo_bot.log`
- [ ] Verify integration points still work (scene_images.py can still call the method)

If you encounter issues:
- [ ] Document the problem in this handoff
- [ ] Check if it's a dependency issue (API key, library version)
- [ ] Ask for clarification rather than guessing (especially about API endpoints)

---

## PROGRESS TRACKING

### Completed:
- [ ] Task analysis complete
- [ ] Implementation started
- [ ] Core functionality working
- [ ] Testing complete
- [ ] Integration verified

### Blockers:
None yet

### Notes:
- Research needed: Which Google API endpoint for image generation? Is it Gemini Imagen, or a different service?
- The `google.generativeai` library is already imported and configured
- May need to check Google's documentation for image generation API

---

## NEXT STEPS FOR SPECIALIST

1. Review this handoff and all reference documents
2. Understand the safety guards and file boundaries (only modify generate_image method)
3. Review existing code patterns (ask_gemini, ask_mistral for async/error handling)
4. Research Gemini Imagen API or Google image generation API
5. Implement the API call in generate_image() method
6. Test thoroughly in Discord
7. Update this handoff with progress
8. Mark as complete when done

---

**End of Specialist Handoff**

*For the forgotten 99%, we rise.* 🔥

