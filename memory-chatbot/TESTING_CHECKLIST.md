# Testing Checklist

Use this checklist to validate that your Memory-Based Chatbot is working correctly.

## Pre-Flight Checks

### Infrastructure
- [ ] Docker is installed and running
- [ ] Python 3.8+ is installed
- [ ] Virtual environment created
- [ ] All dependencies installed (`pip install -r requirements.txt`)

### Configuration
- [ ] `.env` file created (or using UI input)
- [ ] OpenAI API key is valid and active
- [ ] Qdrant container is running (`docker ps | grep qdrant`)
- [ ] Qdrant web UI is accessible (http://localhost:6334)

## Functional Testing

### 1. Application Startup
- [ ] Run `streamlit run app.py` without errors
- [ ] Application loads in browser (http://localhost:8501)
- [ ] No error messages in terminal or UI
- [ ] Sidebar displays configuration section

### 2. Configuration Validation
- [ ] Can enter API key in sidebar
- [ ] Invalid API key shows error message
- [ ] Valid API key shows success message
- [ ] Can select different models from dropdown

### 3. User Authentication
- [ ] Can enter username in sidebar
- [ ] Username is displayed as "Logged in as: [username]"
- [ ] Cannot chat without entering username

### 4. Basic Chat Functionality
- [ ] Can type message in chat input
- [ ] Message appears in chat interface
- [ ] Bot responds to message
- [ ] Response appears in chat interface
- [ ] Chat history persists during session

### 5. Memory Storage
**Test 1: Store Simple Information**
```
User: My favorite color is blue
Expected: Bot acknowledges and stores
```
- [ ] Bot responds appropriately
- [ ] Memory counter in sidebar increases
- [ ] Can view memory in "View All Memories"

**Test 2: Store Multiple Facts**
```
User: I work as a software engineer
User: I live in San Francisco
User: I have a dog named Max
```
- [ ] All facts stored separately
- [ ] Memory count shows correct number
- [ ] Each memory visible in "View All Memories"

### 6. Memory Retrieval
**Test 3: Recall Stored Information**
```
User: What's my favorite color?
Expected: Your favorite color is blue
```
- [ ] Bot recalls correctly
- [ ] "Retrieved Memories" expander shows relevant memory
- [ ] Response is contextually accurate

**Test 4: Multi-Turn Context**
```
User: What do I do for work?
Expected: You work as a software engineer
User: Where do I live?
Expected: You live in San Francisco
```
- [ ] Both questions answered correctly
- [ ] Each response uses appropriate memory

### 7. Semantic Search
**Test 5: Similar Meaning Queries**
```
Stored: "My favorite color is blue"
Query: "What color do I prefer?"
```
- [ ] Bot finds relevant memory despite different wording
- [ ] Response is accurate
- [ ] Retrieved memories section shows the match

### 8. User Isolation
**Test 6: Different Users**
```
Username: alice
Alice: My favorite food is pizza

[Switch user]
Username: bob
Bob: What's my favorite food?
Expected: Bot says it doesn't know
```
- [ ] Bob doesn't see Alice's memories
- [ ] Memory count for Bob is separate from Alice
- [ ] "View All Memories" shows different data per user

### 9. Memory Statistics
- [ ] "Total Memories" counter is accurate
- [ ] "Last Updated" shows recent timestamp
- [ ] Stats update after each interaction

### 10. Memory Viewing
- [ ] "View All Memories" button works
- [ ] All stored memories are displayed
- [ ] Memories show content and metadata
- [ ] Can expand/collapse each memory

### 11. Memory Export
- [ ] "Export Memories" button works
- [ ] Download button appears
- [ ] Downloaded JSON file is valid
- [ ] JSON contains all memories and metadata
- [ ] Filename includes username and timestamp

**Verify JSON Structure:**
```json
{
  "user_id": "alice",
  "export_timestamp": "2024-...",
  "statistics": {...},
  "memories": [...]
}
```

### 12. Clear Memory
**Test 7: Clear Individual User**
```
Username: alice (has memories)
Click: "Clear All Memories"
Click: "Confirm Clear"
```
- [ ] Confirmation button appears
- [ ] After confirmation, memories are cleared
- [ ] Memory count shows 0
- [ ] "View All Memories" shows empty
- [ ] Chat conversation is cleared
- [ ] Other users' memories unaffected

### 13. Clear Conversation
- [ ] "Clear Conversation" button works
- [ ] Chat display is cleared
- [ ] Memories persist (check sidebar stats)
- [ ] Can continue chatting with memory intact

### 14. Session Persistence
**Test 8: Restart Application**
```
1. Chat with bot, store memories
2. Stop application (Ctrl+C)
3. Restart: streamlit run app.py
4. Login with same username
```
- [ ] Previous memories still exist
- [ ] Can query stored information
- [ ] Memory count is same as before

### 15. Model Selection
- [ ] Can switch between models (gpt-4o, gpt-4-turbo, etc.)
- [ ] Bot works with different models
- [ ] Model preference persists during session

### 16. Error Handling
**Test 9: Network Issues**
```
Turn off internet briefly
Send message
```
- [ ] Error message is displayed
- [ ] Application doesn't crash
- [ ] Can retry after connection restored

**Test 10: Invalid Input**
```
Enter very long message (5000+ characters)
```
- [ ] Application handles gracefully
- [ ] Error shown if message too long
- [ ] Application doesn't crash

**Test 11: Qdrant Down**
```
docker-compose down
Try to use app
```
- [ ] Clear error message shown
- [ ] Helpful hint about starting Qdrant
- [ ] Application doesn't crash

## Edge Cases

### 17. Empty Inputs
- [ ] Cannot send empty message
- [ ] Empty username not accepted

### 18. Special Characters
```
Test with: "I love C++ & Python! #coding @work 😊"
```
- [ ] Special characters handled correctly
- [ ] Emojis stored and retrieved
- [ ] No encoding errors

### 19. Long Conversation
```
Send 20+ messages in sequence
```
- [ ] All messages processed
- [ ] Memory search still works
- [ ] Performance remains acceptable
- [ ] UI remains responsive

### 20. Concurrent Users (Manual)
```
Open app in two different browsers
Login as different users
Chat simultaneously
```
- [ ] Both users work independently
- [ ] No memory mixing
- [ ] No errors or conflicts

## Advanced Validation

### 21. Qdrant Integration
**Check in Qdrant Web UI (http://localhost:6334)**
- [ ] Collection "memory_chatbot" exists
- [ ] Collection has vectors stored
- [ ] Point count matches memory count
- [ ] Can view vector data
- [ ] Metadata is attached to vectors

### 22. Memory Quality
**Test 10: Complex Context**
```
User: I'm planning a trip to Japan next month
User: I need to learn some Japanese phrases
User: What are my travel plans?
Expected: Bot mentions Japan trip
```
- [ ] Bot maintains context across messages
- [ ] Retrieved memories are relevant
- [ ] Response is coherent and accurate

### 23. Performance
- [ ] Initial load < 5 seconds
- [ ] Message response < 5 seconds (with good internet)
- [ ] Memory search is fast (< 1 second)
- [ ] UI remains responsive during processing

## Code Quality Checks

### 24. Code Validation
```bash
python3 -m py_compile config.py
python3 -m py_compile memory_manager.py
python3 -m py_compile app.py
```
- [ ] All files compile without syntax errors

### 25. File Structure
- [ ] All required files present:
  - [ ] app.py
  - [ ] config.py
  - [ ] memory_manager.py
  - [ ] requirements.txt
  - [ ] docker-compose.yml
  - [ ] .env.example
  - [ ] .gitignore
  - [ ] README.md
  - [ ] SETUP_GUIDE.md
  - [ ] TESTING_CHECKLIST.md

### 26. Documentation
- [ ] README.md is comprehensive
- [ ] SETUP_GUIDE.md is clear
- [ ] Code has helpful comments
- [ ] .env.example has all required variables

## Final Verification

### 27. Complete User Journey
**End-to-End Test:**
1. [ ] Fresh start (new username)
2. [ ] First conversation (store 3+ facts)
3. [ ] Second conversation (recall facts)
4. [ ] View all memories
5. [ ] Export memories
6. [ ] Restart app
7. [ ] Login again (verify persistence)
8. [ ] Clear memories
9. [ ] Verify empty state

### 28. Multi-User Scenario
1. [ ] User A stores preferences
2. [ ] User B stores different preferences
3. [ ] User A recalls correctly
4. [ ] User B recalls correctly
5. [ ] No data leakage between users

## Sign-Off Checklist

After completing all tests above:

- [ ] All core features work as expected
- [ ] No critical bugs or crashes
- [ ] Memory persistence works across sessions
- [ ] User isolation is functioning
- [ ] Error handling is appropriate
- [ ] Documentation is accurate
- [ ] Ready for use/demonstration

## Known Limitations

Document any issues found during testing:

1. ____________________________________
2. ____________________________________
3. ____________________________________

## Test Environment

- **Date Tested**: _______________
- **Python Version**: _______________
- **OS**: _______________
- **Docker Version**: _______________
- **Tester**: _______________

---

## Quick Smoke Test (5 minutes)

If you're short on time, run this minimal test:

1. [ ] Start Qdrant: `docker-compose up -d`
2. [ ] Run app: `streamlit run app.py`
3. [ ] Enter API key and username
4. [ ] Send: "My favorite color is blue"
5. [ ] Ask: "What's my favorite color?" → Should say blue
6. [ ] Check memory count in sidebar → Should show memories
7. [ ] Export memories → Should download JSON
8. [ ] Switch username → Should have empty memory
9. [ ] Return to first username → Should still have memories

If all 9 steps pass, your core implementation is working!

---

**Testing Complete?** Great! Now you can start experimenting and learning from the code.
