# Quizzer - Product Roadmap

## Current Status
✅ **v1.0 - Core Functionality Complete**
- CSV to JSON quiz conversion with encoding support
- Interactive CLI quiz runner
- Automatic even distribution of questions across quizzes
- HTML and text report generation
- Auto-selection of latest quiz
- Organized quiz storage by source file

---

## Planned Features

### 🎯 High Priority

#### 1. Question Explanations (3rd Column Support)
**Status**: Planned  
**Description**: Add optional 3rd column in CSV for answer explanations

**Features**:
- Support CSV format: `Question, Answer, Explanation`
- Store explanations in quiz JSON
- Display explanations in failure reports
- Show "Why this is correct" section for each failed question
- Backward compatible (works without 3rd column)

**Example**:
```csv
Question,Answer,Explanation
What is the capital of France?,Paris,"Paris has been the capital of France since 987 AD when Hugh Capet made it his capital."
What are primary colors?,"red,blue,yellow","Primary colors cannot be created by mixing other colors. They are the base for all other colors in the color wheel."
```

**Benefits**:
- Learn from mistakes with detailed explanations
- Better understanding of correct answers
- Educational value beyond simple Q&A

---

#### 2. Review Mode
**Status**: Planned  
**Description**: Interactive learning mode with immediate feedback

**Features**:
- New flag: `python run_quiz.py --review` or `-r`
- After each answer, show:
  - ✅/❌ Correct/Incorrect indicator
  - The correct answer
  - Explanation (if available)
  - "Press Enter for next question" prompt
- No pass/fail at the end (all questions shown)
- Optional: Show running score during quiz
- Save review session results separately

**Use Cases**:
- Study mode for learning material
- Self-paced practice without pressure
- Understanding concepts before taking graded quiz

**UI Example**:
```
Question 1/50: What is the capital of France?
Your answer: paris
✅ Correct!

Explanation: Paris has been the capital of France since 987 AD...

[Press Enter to continue]
```

---

#### 3. Enhanced Reporting
**Status**: Planned  
**Description**: Richer report content with explanations

**Features**:
- Add "Explanation" section to HTML reports
- Show explanation for ALL questions (not just failures)
- Collapsible sections for passed questions
- Color-coded explanations
- Export report as PDF option
- Email report functionality

---

### 🚀 Medium Priority

#### 4. Question Difficulty Levels
**Status**: Idea  
**Description**: Add difficulty rating to questions

**Features**:
- Optional 4th column: `Question,Answer,Explanation,Difficulty`
- Difficulty levels: Easy, Medium, Hard (or 1-5 scale)
- Filter quizzes by difficulty
- Progressive learning mode (start easy, increase difficulty)
- Difficulty-weighted scoring

**Example**:
```bash
python import_quiz.py input.csv --difficulty medium,hard
python run_quiz.py --difficulty-range easy-medium
```

---

#### 5. Question Categories/Tags
**Status**: Idea  
**Description**: Organize questions by topic or category

**Features**:
- Optional column: `Question,Answer,Explanation,Tags`
- Tags: comma-separated (e.g., "networking,dns,security")
- Generate quizzes filtered by tags
- Category-based statistics
- Topic-focused study sessions

**Example**:
```bash
python import_quiz.py az-104.csv --tags "networking,compute"
python run_quiz.py --tags networking --max-questions 20
```

---

#### 6. Spaced Repetition Algorithm
**Status**: Idea  
**Description**: Smart question scheduling based on performance

**Features**:
- Track individual question performance history
- Prioritize previously failed questions
- SM-2 or Leitner algorithm implementation
- Optimal review intervals
- Adaptive difficulty adjustment

**Benefits**:
- More efficient learning
- Focus on weak areas
- Long-term retention improvement

---

#### 7. Timed Quiz Mode
**Status**: Idea  
**Description**: Add time limits and tracking

**Features**:
- Quiz-level time limit
- Per-question time tracking
- Time pressure mode
- Leaderboard/best times
- Time statistics in reports

**Example**:
```bash
python run_quiz.py --time-limit 30  # 30 minutes total
python run_quiz.py --per-question-time 60  # 60 seconds each
```

---

#### 8. Multi-Choice Question Support
**Status**: Idea  
**Description**: Support multiple-choice format beyond text input

**Features**:
- CSV column: `Question,Answer,Choices,Explanation`
- Display options A, B, C, D
- Randomize choice order
- Support multiple correct answers
- Select by letter or number

**Example Format**:
```csv
Question,Answer,Choices,Explanation
"What are primary colors?","A,C,D","A:Red|B:Green|C:Blue|D:Yellow","RGB is for light, RBY is for pigments"
```

---

### 💡 Nice-to-Have Features

#### 9. Web UI / Progressive Web App
**Status**: Future  
**Description**: Browser-based interface

**Features**:
- Flask/FastAPI backend
- Responsive web interface
- Mobile-friendly design
- No installation required
- Cloud storage integration
- Multi-user support with accounts

---

#### 10. Question Media Support
**Status**: Future  
**Description**: Images, diagrams, and code snippets

**Features**:
- Image URLs in questions
- Code syntax highlighting
- Diagram support (Mermaid, PlantUML)
- Audio clips for language learning
- LaTeX math equations

---

#### 11. Collaborative Features
**Status**: Future  
**Description**: Share and compete with others

**Features**:
- Share quiz results via URL
- Leaderboards
- Challenge friends
- Group study sessions
- Peer-created question pools
- Question rating/voting system

---

#### 12. AI-Powered Features
**Status**: Future  
**Description**: Leverage AI for enhanced learning

**Features**:
- Auto-generate explanations from answers
- Suggest related questions
- Generate quizzes from study materials (PDFs, notes)
- Adaptive difficulty based on AI analysis
- Natural language answer matching (fuzzy matching)
- Voice input/output support

---

#### 13. Analytics Dashboard
**Status**: Future  
**Description**: Comprehensive performance tracking

**Features**:
- Historical performance graphs
- Strength/weakness analysis
- Topic mastery percentage
- Study time tracking
- Progress over time visualization
- Predictive pass/fail likelihood

---

#### 14. Integration Features
**Status**: Future  
**Description**: Connect with external tools

**Features**:
- Import from Anki decks
- Export to Quizlet
- Google Sheets integration
- Notion database sync
- GitHub Actions for automated testing
- Slack/Discord notifications

---

#### 15. Gamification
**Status**: Future  
**Description**: Make learning fun and engaging

**Features**:
- Achievement badges
- Streak tracking
- XP points and levels
- Daily challenges
- Reward system
- Study goals and milestones

---

#### 16. Custom Answer Validators
**Status**: Future  
**Description**: Flexible answer validation rules

**Features**:
- Regex-based answer matching
- Numeric range validation (e.g., "±5")
- Case-sensitive/insensitive toggle per question
- Synonym support (configurable)
- Partial credit for multi-part answers
- Custom validation scripts

---

#### 17. Study Session Management
**Status**: Future  
**Description**: Organize and track study sessions

**Features**:
- Create study plans (e.g., "AZ-104 30-day plan")
- Session scheduling and reminders
- Pomodoro timer integration
- Break reminders
- Session notes and reflections
- Study buddy pairing

---

#### 18. Offline Mode
**Status**: Future  
**Description**: Full functionality without internet

**Features**:
- Offline web app (PWA)
- Local database sync
- Download quizzes for offline use
- Sync results when online
- Mobile app (React Native/Flutter)

---

## Technical Improvements

### Code Quality
- [ ] Add type hints to all functions
- [ ] Improve test coverage to 90%+
- [ ] Add integration tests
- [ ] Performance benchmarking
- [ ] Memory usage optimization
- [ ] Async quiz loading for large files

### Documentation
- [ ] API documentation (if web backend added)
- [ ] Video tutorials
- [ ] Contributing guide
- [ ] Architecture documentation
- [ ] User manual with screenshots

### DevOps
- [ ] Docker containerization
- [ ] CI/CD pipeline improvements
- [ ] Automated release process
- [ ] Performance monitoring
- [ ] Error tracking (Sentry)

---

## Version Planning

### v1.1 (Next Release)
- ✨ Question explanations (3rd column)
- ✨ Review mode
- ✨ Enhanced HTML reports with explanations

### v1.2
- ✨ Question difficulty levels
- ✨ Categories/tags support
- ✨ Timed quiz mode

### v1.3
- ✨ Spaced repetition algorithm
- ✨ Multi-choice question support
- ✨ Analytics dashboard

### v2.0 (Major Release)
- ✨ Web UI
- ✨ Multi-user support
- ✨ Cloud storage
- ✨ Mobile app

---

## Contributing Ideas

Have a feature idea not listed here? 

1. Open an issue on GitHub
2. Start a discussion in Discussions tab
3. Submit a PR with proof-of-concept
4. Vote on existing feature requests

---

## Priority Criteria

Features are prioritized based on:
- **User Impact**: How many users benefit?
- **Development Effort**: Time and complexity required
- **Educational Value**: Does it improve learning outcomes?
- **Feasibility**: Technical constraints and dependencies
- **Community Demand**: Feature requests and votes

---

*Last Updated: February 6, 2026*
