const { useState, useEffect } = React;

      function App() {
        const [currentStep, setCurrentStep] = useState('landing'); 
        const [isLoggedIn, setIsLoggedIn] = useState(false);

        // Login Form Data
        const [studentId, setStudentId] = useState('');
        const [inputName, setInputName] = useState('');
        const [inputGpa, setInputGpa] = useState('');
        const [inputCompletedHours, setInputCompletedHours] = useState('');
        const [inputMajor, setInputMajor] = useState('AIDS'); 

        // Current Student Data
        const [student, setStudent] = useState({
          fullName: 'Layan Alkhawaldeh',
          studentId: '2134567',
          university: 'Hashemite University',
          major: 'AIDS',
          gpa: '3.45',
          completedHours: 72,
          targetGpa: 3.60
        });

        const [selectedCourseIds, setSelectedCourseIds] = useState(['cs_cpp', 'cs_ds', 'cs_db']);
        const [activeTestBankCourseId, setActiveTestBankCourseId] = useState(null);
        const [testBankAnswers, setTestBankAnswers] = useState({});

        const [semesterDates, setSemesterDates] = useState({ start: '', firstExam: '', secondExam: '' });
        const [semesterDatesDraft, setSemesterDatesDraft] = useState({ start: '', firstExam: '', secondExam: '' });

        const [currentWeekIndex, setCurrentWeekIndex] = useState(1);
        const [weekAnswers, setWeekAnswers] = useState({ q1: '', q2: '' });
        const [weekScores, setWeekScores] = useState({});

        const [tasks, setTasks] = useState([
          { id: 1, title: 'Study Chapter 4 of Data Structures', category: 'Academic', priority: 'High', completed: false },
          { id: 2, title: 'Complete backend code for FastAPI Student System', category: 'Projects', priority: 'High', completed: true },
          { id: 3, title: 'Read 10 pages of a technical book', category: 'Habits', priority: 'Medium', completed: false }
        ]);

        const [newTaskTitle, setNewTaskTitle] = useState('');
        const [newTaskCategory, setNewTaskCategory] = useState('Academic');
        const [newTaskPriority, setNewTaskPriority] = useState('Medium');

        const [emergencyReason, setEmergencyReason] = useState('');
        const [availableHours, setAvailableHours] = useState('2');
        const [aiEmergencyPlan, setAiEmergencyPlan] = useState(null);
        const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);

        const TOTAL_CHAPTERS = 8;
        const [chapterProgress, setChapterProgress] = useState({}); 
        const [activeChaptersCourseId, setActiveChaptersCourseId] = useState(null);

        const POMODORO_PRESETS = {
          '25_5': { study: 25 * 60, brk: 5 * 60, label: '25 / 5' },
          '50_10': { study: 50 * 60, brk: 10 * 60, label: '50 / 10' }
        };
        const [pomodoroMode, setPomodoroMode] = useState('25_5'); 
        const [customStudyMin, setCustomStudyMin] = useState(25);
        const [customBreakMin, setCustomBreakMin] = useState(5);
        const [pomodoroPhase, setPomodoroPhase] = useState('study'); 
        const [pomodoroSecondsLeft, setPomodoroSecondsLeft] = useState(25 * 60);
        const [pomodoroRunning, setPomodoroRunning] = useState(false);
        const [pomodoroSessionsCompleted, setPomodoroSessionsCompleted] = useState(0);
        const pomodoroDurationsRef = React.useRef({ study: 25 * 60, brk: 5 * 60 });

        const [examEvents, setExamEvents] = useState([]); 
        const [examDraft, setExamDraft] = useState({ courseId: '', date: '', time: '10:00', location: '' });
        const [calendarViewDate, setCalendarViewDate] = useState(new Date());
        const [nowTick, setNowTick] = useState(new Date());

        // GPA Calculator states
        const [gpaPrev, setGpaPrev] = useState('');
        const [hoursPrev, setHoursPrev] = useState('');
        const [gpaCourses, setGpaCourses] = useState([]);

        const currentMajorCourses = IT_MAJORS[student.major]?.courses || [];
        const selectedCourses = currentMajorCourses.filter(c => selectedCourseIds.includes(c.id));
        const totalCredits = selectedCourses.reduce((sum, c) => sum + c.credits, 0);

        const majorTotalCredits = IT_MAJORS[student.major]?.courses.reduce((sum, c) => sum + c.credits, 0) || 132;
        const currentGpaVal = parseFloat(student.gpa) || 0;
        const completedHrsVal = parseInt(student.completedHours) || 0;
        const remainingHrsVal = Math.max(0, majorTotalCredits - completedHrsVal);

        const maxPossibleGpa = remainingHrsVal > 0 
          ? ((currentGpaVal * completedHrsVal) + (4.0 * remainingHrsVal)) / majorTotalCredits 
          : currentGpaVal;
        const maxGpaFormatted = Math.min(4.00, Math.round(maxPossibleGpa * 100) / 100);
        const targetGpaVal = parseFloat(student.targetGpa) || 0;
        const isTargetGpaImpossible = targetGpaVal > maxPossibleGpa;

        const requiredGpaVal = remainingHrsVal > 0
          ? ((targetGpaVal * majorTotalCredits) - (currentGpaVal * completedHrsVal)) / remainingHrsVal
          : null;

        // Auto Sync state with backend on login
        useEffect(() => {
          if (!isLoggedIn || !student.studentId) return;
          const loadData = async () => {
            const resData = await apiCall(`/profile/${student.studentId}`);
            if (resData) {
              setStudent(resData.profile || student);
              setSelectedCourseIds(resData.selectedCourseIds || []);
              setSemesterDates(resData.semesterDates || { start: '', firstExam: '', secondExam: '' });
              setTasks(resData.tasks || []);
              setChapterProgress(resData.chapterProgress || {});
              setPomodoroSessionsCompleted(resData.pomodoroSessions || 0);
              setWeekScores(resData.quizScores || {});
              if (resData.examEvents) {
                setExamEvents(resData.examEvents.map(e => ({ ...e, dt: new Date(`${e.date}T${e.time}:00`) })));
              }
            }
            // Load GPA calculator data
            const resGpa = await apiCall(`/gpa/${student.studentId}`);
            if (resGpa) {
              setGpaPrev(resGpa.gpaPrev !== undefined ? resGpa.gpaPrev : '');
              setHoursPrev(resGpa.hoursPrev !== undefined ? resGpa.hoursPrev : '');
              if (resGpa.gpaCourses && resGpa.gpaCourses.length > 0) {
                setGpaCourses(resGpa.gpaCourses);
              }
            }
          };
          loadData();
        }, [isLoggedIn, student.studentId]);

        // Auto save GPA state when modified
        useEffect(() => {
          if (!isLoggedIn || !student.studentId || gpaCourses.length === 0) return;
          const saveGpa = async () => {
            await apiCall(`/gpa/${student.studentId}`, {
              method: 'POST',
              body: JSON.stringify({
                gpaPrev: gpaPrev.toString(),
                hoursPrev: parseInt(hoursPrev) || 0,
                gpaCourses: gpaCourses
              })
            });
          };
          
          const timeoutId = setTimeout(saveGpa, 800);
          return () => clearTimeout(timeoutId);
        }, [gpaPrev, hoursPrev, gpaCourses, isLoggedIn, student.studentId]);

        // Initialize GPA courses from Planner if not set
        useEffect(() => {
          if (isLoggedIn && selectedCourses.length > 0 && gpaCourses.length === 0) {
            setGpaCourses(selectedCourses.map(c => ({
              id: c.id,
              name: c.name,
              credits: c.credits,
              grade: '',
              isRepeat: false,
              prevGrade: ''
            })));
          }
        }, [isLoggedIn, selectedCourseIds, gpaCourses.length]);

        const calculateGpa = () => {
          let semPointsSum = 0;
          let semCreditsSum = 0;

          let prevPointsSum = (parseFloat(gpaPrev) || 0) * (parseInt(hoursPrev) || 0);
          let prevHoursSum = (parseInt(hoursPrev) || 0);

          gpaCourses.forEach(c => {
            const gradeVal = GRADE_POINTS[c.grade];
            if (gradeVal !== undefined) {
              const credits = parseInt(c.credits) || 0;
              semPointsSum += (gradeVal * credits);
              semCreditsSum += credits;

              if (c.isRepeat) {
                const oldGradeVal = GRADE_POINTS[c.prevGrade] || 0;
                prevPointsSum -= (oldGradeVal * credits);
              }
            }
          });

          const semesterGpa = semCreditsSum > 0 ? (semPointsSum / semCreditsSum) : 0;
          
          let totalCumPoints = prevPointsSum;
          let totalCumHours = prevHoursSum;

          gpaCourses.forEach(c => {
            const gradeVal = GRADE_POINTS[c.grade];
            if (gradeVal !== undefined) {
              const credits = parseInt(c.credits) || 0;
              totalCumPoints += (gradeVal * credits);
              if (!c.isRepeat) {
                totalCumHours += credits;
              }
            }
          });

          const cumulativeGpa = totalCumHours > 0 ? (totalCumPoints / totalCumHours) : 0;

          return {
            semesterGpa: semesterGpa.toFixed(2),
            cumulativeGpa: cumulativeGpa.toFixed(2),
            semCreditsSum,
            totalCumHours
          };
        };

        const gpaResults = calculateGpa();

        useEffect(() => {
          if (selectedCourseIds.length > 0) {
            const validIds = selectedCourses.map(c => c.id);
            if (!activeTestBankCourseId || !validIds.includes(activeTestBankCourseId)) {
              setActiveTestBankCourseId(validIds[0]);
            }
          } else {
            setActiveTestBankCourseId(null);
          }
        }, [selectedCourseIds]);

        useEffect(() => {
          if (selectedCourseIds.length > 0) {
            const validIds = selectedCourses.map(c => c.id);
            if (!activeChaptersCourseId || !validIds.includes(activeChaptersCourseId)) {
              setActiveChaptersCourseId(validIds[0]);
            }
          } else {
            setActiveChaptersCourseId(null);
          }
        }, [selectedCourseIds]);

        useEffect(() => {
          const clockId = setInterval(() => setNowTick(new Date()), 1000);
          return () => clearInterval(clockId);
        }, []);

        useEffect(() => {
          pomodoroDurationsRef.current = pomodoroMode === 'custom'
            ? { study: Math.max(1, parseInt(customStudyMin) || 25) * 60, brk: Math.max(1, parseInt(customBreakMin) || 5) * 60 }
            : POMODORO_PRESETS[pomodoroMode];
        }, [pomodoroMode, customStudyMin, customBreakMin]);

                    const now = audioCtx.currentTime;
            // Play 3 sets of rapid double-beeps (Alarm style: Beep-Beep ... Beep-Beep ... Beep-Beep)
            for (let i = 0; i < 3; i++) {
              const timeOffset = i * 0.65;
              playTone(987.77, 0.12, now + timeOffset);        // Beep 1
              playTone(987.77, 0.12, now + timeOffset + 0.18); // Beep 2
            }
          } catch (e) {
            console.warn("Audio play blocked/unsupported: ", e);
          }
        };

        useEffect(() => {
          if (!pomodoroRunning) return;
          const tickId = setInterval(() => {
            setPomodoroSecondsLeft(prev => {
              if (prev > 1) return prev - 1;
              
              playTimerRingSound();
              
              setPomodoroPhase(prevPhase => {
                const nextPhase = prevPhase === 'study' ? 'break' : 'study';
                if (prevPhase === 'study') {
                  setPomodoroSessionsCompleted(c => {
                    const nextVal = c + 1;
                    apiCall(`/pomodoro/${student.studentId}`, { method: 'POST' });
                    return nextVal;
                  });
                }
                return nextPhase;
              });
              return 0;
            });
          }, 1000);
          return () => clearInterval(tickId);
        }, [pomodoroRunning]);

        useEffect(() => {
          const d = pomodoroDurationsRef.current;
          setPomodoroSecondsLeft(pomodoroPhase === 'study' ? d.study : d.brk);
        }, [pomodoroPhase]);

                const buildSemesterPlan = () => {
          const startDate = parseDate(semesterDates.start);
          const firstExamDate = parseDate(semesterDates.firstExam);
          const secondExamDate = parseDate(semesterDates.secondExam);
          if (!startDate || !firstExamDate || !secondExamDate) return null;

          const firstExamWeek = Math.max(2, weekIndexForDate(startDate, firstExamDate));
          const secondExamWeek = Math.max(firstExamWeek + 2, weekIndexForDate(startDate, secondExamDate));
          const totalWeeks = secondExamWeek;

          const weeks = [];
          for (let w = 1; w <= totalWeeks; w++) {
            let type = 'study';
            if (w === firstExamWeek) type = 'exam1';
            else if (w === secondExamWeek) type = 'exam2';
            else if (w === firstExamWeek - 1) type = 'review1';
            else if (w === secondExamWeek - 1) type = 'review2';

            let phaseIndex = w < firstExamWeek ? w - 1 : w - firstExamWeek - 1;

            const coursesPlan = selectedCourses.map(course => {
              if (type === 'exam1' || type === 'exam2') return { course, topics: [] };
              if (type === 'review1' || type === 'review2') {
                return {
                  course,
                  topics: [
                    `Full review of everything covered so far in ${course.name}`,
                    'Solve extra practice problems & past exam-style questions',
                    'Identify and close any remaining weak spots before the exam'
                  ]
                };
              }
              const lecture = LECTURE_TEMPLATES[((phaseIndex % LECTURE_TEMPLATES.length) + LECTURE_TEMPLATES.length) % LECTURE_TEMPLATES.length];
              return {
                course,
                topics: [
                  `Lecture: ${lecture}`,
                  `Practical Lab: Hands-on exercises on "${lecture}"`
                ]
              };
            });

            weeks.push({ weekNumber: w, type, coursesPlan });
          }
          return { weeks, firstExamWeek, secondExamWeek, totalWeeks };
        };

        const semesterPlan = buildSemesterPlan();
        const currentWeekData = semesterPlan ? semesterPlan.weeks.find(w => w.weekNumber === currentWeekIndex) : null;

        const handleLogin = async (e) => {
          e.preventDefault();
          if (studentId.trim() && inputName.trim()) {
            const gpaVal = parseFloat(inputGpa);
            if (!isNaN(gpaVal) && (gpaVal < 0 || gpaVal > 4.0)) {
              alert("Cumulative GPA must be between 0.0 and 4.0");
              return;
            }
            const hoursVal = parseInt(inputCompletedHours);
            if (!isNaN(hoursVal) && (hoursVal < 0 || hoursVal > 150)) {
              alert("Completed Hours must be between 0 and 150");
              return;
            }

            const loginPayload = {
              studentId: studentId,
              fullName: inputName,
              major: inputMajor,
              gpa: inputGpa,
              completedHours: hoursVal
            };

            const backendData = await apiCall("/login", {
              method: "POST",
              body: JSON.stringify(loginPayload)
            });

            if (backendData && backendData.data) {
              const sData = backendData.data;
              setStudent(sData.profile);
              setSelectedCourseIds(sData.selectedCourseIds || []);
              setSemesterDates(sData.semesterDates || { start: '', firstExam: '', secondExam: '' });
              setTasks(sData.tasks || []);
              setChapterProgress(sData.chapterProgress || {});
              setPomodoroSessionsCompleted(sData.pomodoroSessions || 0);
              setWeekScores(sData.quizScores || {});
              if (sData.examEvents) {
                setExamEvents(sData.examEvents.map(ev => ({ ...ev, dt: new Date(`${ev.date}T${ev.time}:00`) })));
              }
            } else {
              setStudent({
                fullName: inputName,
                studentId: studentId,
                university: 'Hashemite University',
                major: inputMajor,
                gpa: inputGpa,
                completedHours: hoursVal,
                targetGpa: roundVal(min(4.0, gpaVal + 0.2))
              });
              const majorCourses = IT_MAJORS[inputMajor]?.courses || [];
              setSelectedCourseIds(majorCourses.slice(0, 3).map(c => c.id));
            }
            setIsLoggedIn(true);
            setCurrentStep('planner');
          }
        };

        const handleUpdateProfile = async (updatedStudent) => {
          setStudent(updatedStudent);
          await apiCall(`/profile/${student.studentId}`, {
            method: "PUT",
            body: JSON.stringify({
              fullName: updatedStudent.fullName,
              major: updatedStudent.major,
              gpa: updatedStudent.gpa,
              completedHours: updatedStudent.completedHours,
              targetGpa: updatedStudent.targetGpa.toString()
            })
          });
        };

        const handleAddTask = async (e) => {
          e.preventDefault();
          if (!newTaskTitle.trim()) return;

          const res = await apiCall(`/tasks/${student.studentId}`, {
            method: "POST",
            body: JSON.stringify({
              title: newTaskTitle,
              category: newTaskCategory,
              priority: newTaskPriority
            })
          });

          if (res && res.task) {
            setTasks([res.task, ...tasks]);
          } else {
            const newTask = {
              id: Date.now(),
              title: newTaskTitle,
              category: newTaskCategory,
              priority: newTaskPriority,
              completed: false
            };
            setTasks([newTask, ...tasks]);
          }
          setNewTaskTitle('');
        };

        const toggleTask = async (id) => {
          setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
          await apiCall(`/tasks/${student.studentId}/${id}`, { method: "PUT" });
        };

        const deleteTask = async (id) => {
          setTasks(tasks.filter(t => t.id !== id));
          await apiCall(`/tasks/${student.studentId}/${id}`, { method: "DELETE" });
        };

        const handleSemesterSetupSubmit = async (e) => {
          e.preventDefault();
          setSemesterDates(semesterDatesDraft);
          
          await apiCall(`/semester-setup/${student.studentId}`, {
            method: "POST",
            body: JSON.stringify({
              start: semesterDatesDraft.start,
              firstExam: semesterDatesDraft.firstExam,
              secondExam: semesterDatesDraft.secondExam,
              selectedCourseIds: selectedCourseIds
            })
          });

          setCurrentWeekIndex(1);
          setWeekScores({});
          setWeekAnswers({ q1: '', q2: '' });
          setCurrentStep('week_plan');
        };

        const handleWeekQuizSubmit = async (e) => {
          e.preventDefault();
          let correct = 0;
          if (weekAnswers.q1 === 'correct') correct++;
          if (weekAnswers.q2 === 'correct') correct++;
          const score = (correct / 2) * 100;
          setWeekScores({ ...weekScores, [currentWeekIndex]: score });

          await apiCall(`/quiz-score/${student.studentId}`, {
            method: "POST",
            body: JSON.stringify({
              weekIndex: currentWeekIndex,
              score: score
            })
          });
        };

        const retakeWeekQuiz = () => {
          const updated = { ...weekScores };
          delete updated[currentWeekIndex];
          setWeekScores(updated);
          setWeekAnswers({ q1: '', q2: '' });
        };

        const goToNextWeek = () => {
          const nextIndex = currentWeekIndex + 1;
          setWeekAnswers({ q1: '', q2: '' });
          if (semesterPlan && nextIndex > semesterPlan.totalWeeks) {
            setCurrentStep('planner');
          } else {
            setCurrentWeekIndex(nextIndex);
            setCurrentStep('week_plan');
          }
        };

        const handleGenerateEmergencyPlan = async () => {
          if (!emergencyReason.trim()) return;
          setIsGeneratingPlan(true);

          const res = await apiCall(`/emergency-plan/${student.studentId}`, {
            method: "POST",
            body: JSON.stringify({
              reason: emergencyReason,
              availableHours: availableHours
            })
          });

          if (res) {
            setAiEmergencyPlan(res);
          } else {
            setAiEmergencyPlan({
              summary: `Emergency plan set for ${availableHours} hours based on your situation (${emergencyReason}):`,
              urgentTasks: [
                'Prioritize key concepts from registered courses: Study summaries for 1 hour.',
                'Practice high-yield questions in the Test Bank tab for 45 minutes.',
                'Postpone non-urgent tasks to tomorrow and get rest.'
              ],
              advice: 'Emergency situations are normal! Prioritize core material, stay calm, and rest 🤍'
            });
          }
          setIsGeneratingPlan(false);
        };

        const selectTestBankAnswer = (courseId, qIdx, optIdx) => {
          setTestBankAnswers(prev => ({
            ...prev,
            [courseId]: {
              ...(prev[courseId] || {}),
              [qIdx]: optIdx
            }
          }));
        };

        const resetCourseQuiz = (courseId) => {
          setTestBankAnswers(prev => {
            const updated = { ...prev };
            delete updated[courseId];
            return updated;
          });
        };

        const calculateCourseScore = (courseId) => {
          const courseAns = testBankAnswers[courseId];
          if (!courseAns) return null;
          const questions = TEST_BANK_QUESTIONS[courseId] || getFallbackQuestions('Course');
          const totalQ = questions.length;
          let correct = 0;
          Object.entries(courseAns).forEach(([qIdx, optIdx]) => {
            if (questions[qIdx] && questions[qIdx].correct === optIdx) {
              correct++;
            }
          });
          return Math.round((correct / totalQ) * 100);
        };

        const toggleChapter = async (courseId, chapterNum) => {
          setChapterProgress(prev => {
            const courseState = { ...(prev[courseId] || {}) };
            courseState[chapterNum] = !courseState[chapterNum];
            return { ...prev, [courseId]: courseState };
          });

          await apiCall(`/chapters/${student.studentId}`, {
            method: "POST",
            body: JSON.stringify({
              courseId: courseId,
              chapterNum: chapterNum
            })
          });
        };

        const getCourseChapterPercent = (courseId) => {
          const state = chapterProgress[courseId] || {};
          const doneCount = Object.values(state).filter(Boolean).length;
          return Math.round((doneCount / TOTAL_CHAPTERS) * 100);
        };

        const resetCourseChapters = async (courseId) => {
          setChapterProgress(prev => {
            const updated = { ...prev };
            delete updated[courseId];
            return updated;
          });
          await apiCall(`/chapters/${student.studentId}/${courseId}`, { method: "DELETE" });
        };

        const formatTime = (totalSeconds) => {
          const m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
          const s = (totalSeconds % 60).toString().padStart(2, '0');
          return `${m}:${s}`;
        };

        const applyPomodoroMode = (mode) => {
          setPomodoroMode(mode);
          setPomodoroRunning(false);
          setPomodoroPhase('study');
          const durations = mode === 'custom'
            ? { study: Math.max(1, parseInt(customStudyMin) || 25) * 60, brk: Math.max(1, parseInt(customBreakMin) || 5) * 60 }
            : POMODORO_PRESETS[mode];
          pomodoroDurationsRef.current = durations;
          setPomodoroSecondsLeft(durations.study);
        };

        const applyCustomPomodoro = () => {
          applyPomodoroMode('custom');
        };

        const togglePomodoroRunning = () => setPomodoroRunning(r => !r);

        const resetPomodoro = () => {
          setPomodoroRunning(false);
          setPomodoroPhase('study');
          const d = pomodoroDurationsRef.current;
          setPomodoroSecondsLeft(d.study);
        };

        const skipPomodoroPhase = () => {
          setPomodoroRunning(false);
          setPomodoroPhase(prevPhase => {
            const nextPhase = prevPhase === 'study' ? 'break' : 'study';
            if (prevPhase === 'study') {
              setPomodoroSessionsCompleted(c => {
                const nextVal = c + 1;
                apiCall(`/pomodoro/${student.studentId}`, { method: 'POST' });
                return nextVal;
              });
            }
            return nextPhase;
          });
        };

        const currentPomodoroTotalSeconds = pomodoroPhase === 'study' ? pomodoroDurationsRef.current.study : pomodoroDurationsRef.current.brk;
        const pomodoroProgressPercent = currentPomodoroTotalSeconds > 0
          ? Math.round(((currentPomodoroTotalSeconds - pomodoroSecondsLeft) / currentPomodoroTotalSeconds) * 100)
          : 0;

        const handleAddExam = async (e) => {
          e.preventDefault();
          if (!examDraft.courseId || !examDraft.date) return;

          const res = await apiCall(`/exams/${student.studentId}`, {
            method: "POST",
            body: JSON.stringify({
              courseId: examDraft.courseId,
              date: examDraft.date,
              time: examDraft.time || '10:00',
              location: examDraft.location || 'TBA'
            })
          });

          if (res && res.exam) {
            setExamEvents([...examEvents, {
              ...res.exam,
              dt: new Date(`${res.exam.date}T${res.exam.time}:00`)
            }]);
          } else {
            const course = currentMajorCourses.find(c => c.id === examDraft.courseId);
            setExamEvents([...examEvents, {
              id: Date.now(),
              courseId: examDraft.courseId,
              courseName: course ? course.name : 'Unknown Course',
              date: examDraft.date,
              time: examDraft.time || '10:00',
              location: examDraft.location || 'TBA',
              dt: new Date(`${examDraft.date}T${examDraft.time}:00`)
            }]);
          }
          setExamDraft({ courseId: '', date: '', time: '10:00', location: '' });
        };

        const deleteExam = async (id) => {
          setExamEvents(examEvents.filter(ev => ev.id !== id));
          await apiCall(`/exams/${student.studentId}/${id}`, { method: "DELETE" });
        };

        const changeCalendarMonth = (delta) => {
          setCalendarViewDate(new Date(calendarViewDate.getFullYear(), calendarViewDate.getMonth() + delta, 1));
        };

        const buildMonthGrid = (viewDate) => {
          const year = viewDate.getFullYear();
          const month = viewDate.getMonth();
          const firstDay = new Date(year, month, 1);
          const startWeekday = firstDay.getDay();
          const daysInMonth = new Date(year, month + 1, 0).getDate();
          const cells = [];
          for (let i = 0; i < startWeekday; i++) cells.push(null);
          for (let d = 1; d <= daysInMonth; d++) cells.push(d);
          return cells;
        };

        const pad2 = (n) => n.toString().padStart(2, '0');
        const dateStrForDay = (viewDate, day) => `${viewDate.getFullYear()}-${pad2(viewDate.getMonth() + 1)}-${pad2(day)}`;

        const examsOnDay = (viewDate, day) => {
          if (!day) return [];
          const dateStr = dateStrForDay(viewDate, day);
          return examEvents.filter(ev => ev.date === dateStr);
        };

        const isToday = (viewDate, day) => {
          if (!day) return false;
          const today = new Date();
          return viewDate.getFullYear() === today.getFullYear() &&
                 viewDate.getMonth() === today.getMonth() &&
                 day === today.getDate();
        };

        const upcomingExamsList = examEvents
          .map(ev => ({ ...ev, dt: new Date(`${ev.date}T${ev.time}:00`) }))
          .filter(ev => ev.dt.getTime() >= nowTick.getTime())
          .sort((a, b) => a.dt - b.dt);

        const nextExam = upcomingExamsList[0] || null;

        const getCountdownParts = (targetDate) => {
          const diffMs = Math.max(0, targetDate.getTime() - nowTick.getTime());
          const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
          const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
          return { days, hours, minutes, seconds };
        };

        const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const WEEKDAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

        return (
          <div class="min-h-screen flex flex-col bg-slate-50">
            
            {/* Control Header */}
            {isLoggedIn && (
              <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                  <div class="flex justify-between h-16 items-center">
                    
                    {/* Logo and Platform Name */}
                    <div class="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentStep('planner')}>
                      <div class="w-10 h-10 rounded-xl bg-burgundy-600 flex items-center justify-center text-white shadow-md">
                        <i class="fa-solid fa-graduation-cap text-lg"></i>
                      </div>
                      <div>
                        <span class="font-extrabold text-xl text-slate-900 tracking-tight">EduPulse <span class="text-burgundy-600">AI</span></span>
                        <span class="text-xs block text-slate-400 font-semibold">Smart Academic Platform</span>
                      </div>
                    </div>

                    {/* Main Menu Navigation */}
                    <div class="flex-1 flex justify-center px-4 overflow-x-auto scrollbar-none mx-4">
                      <div class="flex items-center space-x-1 sm:space-x-2 bg-slate-100 p-1.5 rounded-xl border border-slate-200 whitespace-nowrap">
                        
                        <button 
                          onClick={() => setCurrentStep('planner')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${['planner', 'semester_setup', 'week_plan', 'week_quiz'].includes(currentStep) ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-book-open"></i>
                          <span>Planner</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('test_bank')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'test_bank' ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-clipboard-question text-burgundy-600"></i>
                          <span>Test Bank</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('todo')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'todo' ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-list-check text-burgundy-600"></i>
                          <span>To-Do List</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('emergency')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'emergency' ? 'bg-white text-amber-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-wand-magic-sparkles text-amber-500"></i>
                          <span>AI Emergency</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('chapters')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'chapters' ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-layer-group text-burgundy-600"></i>
                          <span>Chapters</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('pomodoro')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'pomodoro' ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-clock text-burgundy-600"></i>
                          <span>Pomodoro</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('exam_calendar')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'exam_calendar' ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-calendar-days text-burgundy-600"></i>
                          <span>Exam Calendar</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('gpa')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'gpa' ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-calculator text-burgundy-600"></i>
                          <span>GPA</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('profile')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'profile' ? 'bg-white text-burgundy-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-user-gear"></i>
                          <span>Profile</span>
                        </button>

                        <button 
                          onClick={() => setCurrentStep('adhkar')} 
                          class={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${currentStep === 'adhkar' ? 'bg-white text-emerald-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                          <i class="fa-solid fa-hands-praying text-emerald-500"></i>
                          <span>الأدعية</span>
                        </button>

                      </div>
                    </div>

                    {/* Student Info & Logout */}
                    <div class="flex items-center space-x-3">
                      <div class="text-left hidden sm:block">
                        <p class="text-xs font-bold text-slate-800">{student.fullName}</p>
                        <p class="text-[11px] text-slate-500 font-semibold">ID: {student.studentId}</p>
                      </div>
                      <button 
                        onClick={() => { setIsLoggedIn(false); setCurrentStep('landing'); }} 
                        title="Logout"
                        class="p-2 text-slate-400 hover:text-red-600 transition-all">
                        <i class="fa-solid fa-right-from-bracket text-base"></i>
                      </button>
                    </div>

                  </div>
                </div>
              </header>
            )}

            {/* Page Content */}
            <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">

              {/* 1. LANDING PAGE */}
              {currentStep === 'landing' && (
                <div class="min-h-[80vh] flex flex-col items-center justify-center text-center max-w-4xl mx-auto animate-fade-in">
                  <div class="w-20 h-20 bg-burgundy-50 border border-burgundy-100 rounded-3xl flex items-center justify-center text-burgundy-600 text-4xl mb-6 shadow-xl shadow-burgundy-100/50">
                    <i class="fa-solid fa-graduation-cap"></i>
                  </div>
                  <span class="px-4 py-1.5 rounded-full bg-burgundy-50 text-burgundy-700 text-xs font-bold mb-4 border border-burgundy-100">
                    Smart Academic Assistant Platform
                  </span>
                  <h1 class="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight mb-6">
                    Welcome to <br/><span class="text-burgundy-600">EduPulse AI</span>
                  </h1>
                  <p class="text-base sm:text-lg text-slate-600 max-w-2xl mb-10 leading-relaxed font-medium">
                    The smart academic assistant customized for IT faculty students at Hashemite University to plan study schedules, manage daily tasks, and solve practice questions.
                  </p>
                  <button 
                    onClick={() => setCurrentStep('login')}
                    class="px-10 py-4 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-base rounded-2xl shadow-xl shadow-burgundy-600/30 transition-all transform hover:-translate-y-0.5">
                    Log In to Platform <i class="fa-solid fa-arrow-right ml-2"></i>
                  </button>
                </div>
              )}

              {/* 2. LOGIN PAGE */}
              {currentStep === 'login' && (
                <div class="min-h-[75vh] flex items-center justify-center animate-fade-in">
                  <div class="max-w-md w-full bg-white p-8 rounded-3xl border border-slate-200/80 shadow-2xl">
                    <div class="text-center mb-8">
                      <div class="w-14 h-14 bg-burgundy-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-3 text-xl shadow-lg shadow-burgundy-200">
                        <i class="fa-solid fa-id-card"></i>
                      </div>
                      <h2 class="text-2xl font-extrabold text-slate-900">Student Login</h2>
                      <p class="text-xs text-slate-500 mt-1">Enter your academic details to continue</p>
                    </div>

                    <form onSubmit={handleLogin} class="space-y-4">
                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Full Name</label>
                        <input 
                          type="text" 
                          required
                          value={inputName}
                          onChange={(e) => setInputName(e.target.value)}
                          placeholder="Enter your full name" 
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Student ID</label>
                        <input 
                          type="text" 
                          required
                          value={studentId}
                          onChange={(e) => setStudentId(e.target.value)}
                          placeholder="Example: 2134567" 
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Academic Major</label>
                        <select 
                          value={inputMajor}
                          onChange={(e) => setInputMajor(e.target.value)}
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        >
                          <option value="AIDS">Artificial Intelligence & Data Science (AIDS)</option>
                          <option value="CS">Computer Science (CS)</option>
                          <option value="CIS">Computer Information Systems (CIS)</option>
                          <option value="SWE">Software Engineering (SWE)</option>
                          <option value="BIT">Business Information Technology (BIT)</option>
                          <option value="CYS">Cyber Security (CYS)</option>
                        </select>
                      </div>

                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Current Cumulative GPA (Max 4.00)</label>
                        <input 
                          type="number" 
                          step="0.01"
                          max="4.00"
                          min="0.00"
                          required
                          value={inputGpa}
                          onChange={(e) => setInputGpa(e.target.value)}
                          placeholder="Example: 3.45" 
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Completed Credit Hours</label>
                        <input 
                          type="number" 
                          required
                          min="0"
                          max="150"
                          value={inputCompletedHours}
                          onChange={(e) => setInputCompletedHours(e.target.value)}
                          placeholder="Example: 72" 
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <button 
                        type="submit"
                        class="w-full py-3.5 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-sm rounded-xl shadow-lg shadow-burgundy-600/30 transition-all mt-2">
                        Login to Account
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* 3. COURSE PLANNER PAGE */}
              {currentStep === 'planner' && (
                <div class="space-y-6 animate-fade-in">
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md flex justify-between items-center flex-wrap gap-4">
                    <div>
                      <h2 class="text-2xl font-bold text-slate-900">Semester Course Planner</h2>
                      <p class="text-xs text-slate-500 mt-1">Select courses and calculate credit hours automatically for {IT_MAJORS[student.major]?.name}.</p>
                    </div>
                    <div class="flex items-center gap-3">
                      <span class={`text-lg font-extrabold px-4 py-2 rounded-xl ${totalCredits > 18 ? 'bg-red-100 text-red-700' : 'bg-burgundy-50 text-burgundy-700'}`}>
                        {totalCredits} / 18 Credits
                      </span>
                      <button
                        onClick={() => {
                          setSemesterDatesDraft(semesterDates);
                          setCurrentStep('semester_setup');
                        }}
                        class="px-4 py-2 rounded-xl text-xs font-bold border border-slate-200 text-slate-600 hover:border-burgundy-300 hover:text-burgundy-600 transition-all flex items-center gap-1.5">
                        <i class="fa-solid fa-calendar-days"></i>
                        <span>{semesterDates.start ? 'Edit Exam Dates' : 'Set Exam Dates'}</span>
                      </button>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {currentMajorCourses.map(course => {
                      const isSelected = selectedCourseIds.includes(course.id);
                      return (
                        <div 
                          key={course.id}
                          onClick={() => {
                            if (isSelected) {
                              setSelectedCourseIds(selectedCourseIds.filter(id => id !== course.id));
                            } else {
                              setSelectedCourseIds([...selectedCourseIds, course.id]);
                            }
                          }}
                          class={`p-5 rounded-2xl border transition-all cursor-pointer ${
                            isSelected 
                            ? 'bg-burgundy-50/50 border-burgundy-600 shadow-md' 
                            : 'bg-white border-slate-200 hover:border-slate-300'
                          }`}>
                          <div class="flex justify-between items-start mb-2">
                            <span class={`text-xs font-bold px-2.5 py-1 rounded-lg ${course.credits === 1 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'}`}>
                              {course.credits} {course.credits === 1 ? 'Credit (Lab)' : 'Credits'}
                            </span>
                            <span class="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                              {course.difficulty}
                            </span>
                          </div>
                          <h3 class="font-bold text-slate-900 text-sm mb-1">{course.name}</h3>
                          <p class="text-xs text-slate-400 font-medium">Prerequisite: {course.prerequisite}</p>
                        </div>
                      );
                    })}
                  </div>

                  {/* Continue Button */}
                  <div class="flex justify-end pt-4">
                    <button 
                      onClick={() => {
                        if (semesterDates.start && semesterDates.firstExam && semesterDates.secondExam) {
                          setCurrentStep('week_plan');
                        } else {
                          setSemesterDatesDraft(semesterDates);
                          setCurrentStep('semester_setup');
                        }
                      }}
                      disabled={selectedCourseIds.length === 0}
                      class={`px-8 py-3.5 text-white font-bold rounded-xl shadow-lg transition-all flex items-center gap-2 ${
                        selectedCourseIds.length === 0 ? 'bg-slate-300 cursor-not-allowed' : 'bg-burgundy-600 hover:bg-burgundy-700 shadow-burgundy-600/30'
                      }`}>
                      <span>{semesterDates.start ? `Continue to Week ${currentWeekIndex} Plan` : 'Continue to Semester Plan'}</span>
                      <i class="fa-solid fa-arrow-right"></i>
                    </button>
                  </div>
                </div>
              )}

              {/* 3.1 SEMESTER SETUP PAGE (student enters First/Second exam dates) */}
              {currentStep === 'semester_setup' && (
                <div class="max-w-xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-8 rounded-3xl border border-slate-200/80 shadow-xl">
                    <div class="text-center mb-6">
                      <div class="w-14 h-14 bg-burgundy-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-3 text-xl shadow-lg shadow-burgundy-200">
                        <i class="fa-solid fa-calendar-days"></i>
                      </div>
                      <h2 class="text-2xl font-extrabold text-slate-900">Semester & Exam Dates</h2>
                      <p class="text-xs text-slate-500 mt-1">
                        Tell us your semester start date and your First / Second exam dates, and we'll build a week-by-week
                        plan that finishes each exam's material right on time.
                      </p>
                    </div>

                    <form onSubmit={handleSemesterSetupSubmit} class="space-y-4">
                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Semester Start Date</label>
                        <input
                          type="date"
                          required
                          value={semesterDatesDraft.start}
                          onChange={(e) => setSemesterDatesDraft({ ...semesterDatesDraft, start: e.target.value })}
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">First Exam Date</label>
                        <input
                          type="date"
                          required
                          value={semesterDatesDraft.firstExam}
                          onChange={(e) => setSemesterDatesDraft({ ...semesterDatesDraft, firstExam: e.target.value })}
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Second Exam Date</label>
                        <input
                          type="date"
                          required
                          value={semesterDatesDraft.secondExam}
                          onChange={(e) => setSemesterDatesDraft({ ...semesterDatesDraft, secondExam: e.target.value })}
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <button
                        type="submit"
                        class="w-full py-3.5 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-sm rounded-xl shadow-lg shadow-burgundy-600/30 transition-all mt-2">
                        Build My Semester Plan
                      </button>

                      <button
                        type="button"
                        onClick={() => setCurrentStep('planner')}
                        class="w-full py-2 text-slate-500 hover:text-slate-800 font-bold text-xs transition-all">
                        <i class="fa-solid fa-chevron-left mr-1"></i> Back to Courses
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* 3.2 DYNAMIC WEEKLY PLAN PAGE (covers the whole semester, week by week) */}
              {currentStep === 'week_plan' && (
                <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
                  {!semesterPlan ? (
                    <div class="bg-white p-8 rounded-3xl border border-slate-200/80 shadow-md text-center space-y-4">
                      <p class="text-sm font-bold text-slate-700">Please set your semester and exam dates first.</p>
                      <button
                        onClick={() => { setSemesterDatesDraft(semesterDates); setCurrentStep('semester_setup'); }}
                        class="px-8 py-3 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold rounded-xl shadow-lg transition-all">
                        Set Exam Dates
                      </button>
                    </div>
                  ) : (
                    <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                      <div class="flex flex-wrap justify-between items-center gap-3 mb-4">
                        <div>
                          <span class="text-xs font-bold px-3 py-1 bg-burgundy-50 text-burgundy-700 rounded-full border border-burgundy-100">
                            Week {currentWeekIndex} of {semesterPlan.totalWeeks}
                          </span>
                          <h2 class="text-2xl font-extrabold text-slate-900 mt-2">
                            {currentWeekData.type === 'exam1' && 'First Exam Week'}
                            {currentWeekData.type === 'exam2' && 'Second Exam Week'}
                            {currentWeekData.type === 'review1' && 'Final Review Before the First Exam'}
                            {currentWeekData.type === 'review2' && 'Final Review Before the Second Exam'}
                            {currentWeekData.type === 'study' && `Week ${currentWeekIndex} Study Syllabus`}
                          </h2>
                          <p class="text-xs text-slate-500 mt-1">
                            {currentWeekIndex < semesterPlan.firstExamWeek && `${semesterPlan.firstExamWeek - currentWeekIndex} week(s) left until your First Exam`}
                            {currentWeekIndex >= semesterPlan.firstExamWeek && currentWeekIndex < semesterPlan.secondExamWeek && `${semesterPlan.secondExamWeek - currentWeekIndex} week(s) left until your Second Exam`}
                            {currentWeekIndex === semesterPlan.secondExamWeek && 'This is the final week of your semester plan'}
                          </p>
                        </div>
                        <button onClick={() => setCurrentStep('planner')} class="text-xs font-bold text-slate-500 hover:text-slate-800">
                          <i class="fa-solid fa-chevron-left mr-1"></i> Back to Courses
                        </button>
                      </div>

                      {(currentWeekData.type === 'exam1' || currentWeekData.type === 'exam2') ? (
                        <div class="my-6 p-6 rounded-2xl bg-amber-50 border border-amber-200 text-center space-y-2">
                          <i class="fa-solid fa-graduation-cap text-amber-500 text-2xl"></i>
                          <p class="text-sm font-bold text-amber-800">
                            {currentWeekData.type === 'exam1' ? 'Good luck in your First Exam this week!' : 'Good luck in your Second Exam this week!'}
                          </p>
                          <p class="text-xs text-amber-700">
                            Keep this week light: get enough sleep, do a final light read-through, and trust the work you already put in.
                          </p>
                        </div>
                      ) : (
                        <div class="space-y-4 my-6">
                          {currentWeekData.type === 'review1' && (
                            <p class="text-xs font-bold text-burgundy-700 bg-burgundy-50 border border-burgundy-100 rounded-xl p-3">
                              📌 This is your last study week before the First Exam — all First Exam material should be finished by the end of this week.
                            </p>
                          )}
                          {currentWeekData.type === 'review2' && (
                            <p class="text-xs font-bold text-burgundy-700 bg-burgundy-50 border border-burgundy-100 rounded-xl p-3">
                              📌 This is your last study week before the Second Exam — wrap up any remaining material now.
                            </p>
                          )}
                          {currentWeekData.coursesPlan.map(({ course, topics }) => (
                            <div key={course.id} class="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                              <h3 class="font-bold text-slate-900 text-sm mb-2">{course.name}</h3>
                              <ul class="text-xs text-slate-600 space-y-1 list-disc list-inside">
                                {topics.map((topic, idx) => (
                                  <li key={idx}>{topic}</li>
                                ))}
                              </ul>
                            </div>
                          ))}
                        </div>
                      )}

                      <div class="flex justify-end pt-4 border-t border-slate-100">
                        {(currentWeekData.type === 'exam1' || currentWeekData.type === 'exam2') ? (
                          <button
                            onClick={goToNextWeek}
                            class="px-8 py-3 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold rounded-xl shadow-lg shadow-burgundy-600/30 transition-all flex items-center gap-2">
                            <span>{currentWeekIndex === semesterPlan.totalWeeks ? 'Finish Semester Plan' : 'Continue to Next Week'}</span>
                            <i class="fa-solid fa-arrow-right"></i>
                          </button>
                        ) : (
                          <button
                            onClick={() => setCurrentStep('week_quiz')}
                            class="px-8 py-3 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold rounded-xl shadow-lg shadow-burgundy-600/30 transition-all flex items-center gap-2">
                            <span>Take Week {currentWeekIndex} Quiz</span>
                            <i class="fa-solid fa-pen-to-square"></i>
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 3.3 DYNAMIC WEEKLY QUIZ PAGE (covers the whole semester, week by week) */}
              {currentStep === 'week_quiz' && semesterPlan && currentWeekData && (
                <div class="max-w-2xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-8 rounded-3xl border border-slate-200/80 shadow-xl">
                    <div class="mb-6 border-b border-slate-100 pb-4">
                      <span class="text-xs font-bold bg-amber-50 text-amber-700 px-3 py-1 rounded-full border border-amber-200">Required Passing Score: &gt; 85%</span>
                      <h2 class="text-2xl font-extrabold text-slate-900 mt-2">Week {currentWeekIndex} Assessment Quiz</h2>
                    </div>

                    {weekScores[currentWeekIndex] === undefined ? (
                      <form onSubmit={handleWeekQuizSubmit} class="space-y-6">
                        <div class="space-y-2">
                          <p class="text-sm font-bold text-slate-800">1. What is the best way to approach this week's material?</p>
                          <label class="flex items-center gap-2 text-xs text-slate-700 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                            <input type="radio" name="q1" value="correct" onChange={(e) => setWeekAnswers({ ...weekAnswers, q1: e.target.value })} required />
                            <span>Building strong, steady understanding through consistent practice</span>
                          </label>
                          <label class="flex items-center gap-2 text-xs text-slate-700 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                            <input type="radio" name="q1" value="wrong" onChange={(e) => setWeekAnswers({ ...weekAnswers, q1: e.target.value })} />
                            <span>Leaving everything to review the night before the exam</span>
                          </label>
                        </div>

                        <div class="space-y-2">
                          <p class="text-sm font-bold text-slate-800">2. How should you apply what you studied this week?</p>
                          <label class="flex items-center gap-2 text-xs text-slate-700 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                            <input type="radio" name="q2" value="wrong" onChange={(e) => setWeekAnswers({ ...weekAnswers, q2: e.target.value })} />
                            <span>Memorizing without any hands-on practice</span>
                          </label>
                          <label class="flex items-center gap-2 text-xs text-slate-700 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                            <input type="radio" name="q2" value="correct" onChange={(e) => setWeekAnswers({ ...weekAnswers, q2: e.target.value })} required />
                            <span>Practicing through labs, exercises, and solved examples</span>
                          </label>
                        </div>

                        <button type="submit" class="w-full py-3 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-sm rounded-xl shadow-lg transition-all">
                          Submit Quiz
                        </button>
                      </form>
                    ) : (
                      <div class="text-center space-y-6 py-4">
                        <div class={`text-4xl font-extrabold ${weekScores[currentWeekIndex] > 85 ? 'text-emerald-600' : 'text-red-600'}`}>
                          {weekScores[currentWeekIndex]}%
                        </div>

                        {weekScores[currentWeekIndex] > 85 ? (
                          <div class="space-y-4">
                            <p class="text-sm text-emerald-700 font-bold bg-emerald-50 p-4 rounded-xl border border-emerald-200">
                              🎉 Congratulations! You scored higher than 85%.
                              {currentWeekIndex === semesterPlan.totalWeeks ? ' You have completed your semester plan!' : ' You can now move on to next week.'}
                            </p>
                            <button
                              onClick={goToNextWeek}
                              class="px-8 py-3 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold rounded-xl shadow-lg transition-all">
                              {currentWeekIndex === semesterPlan.totalWeeks ? 'Finish Semester Plan' : `Continue to Week ${currentWeekIndex + 1} Plan`} <i class="fa-solid fa-arrow-right ml-1"></i>
                            </button>
                          </div>
                        ) : (
                          <div class="space-y-4">
                            <p class="text-sm text-red-700 font-bold bg-red-50 p-4 rounded-xl border border-red-200">
                              ⚠️ Score is lower than 85%. Please review this week's materials and retake the quiz.
                            </p>
                            <button
                              onClick={retakeWeekQuiz}
                              class="px-8 py-3 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl shadow-lg transition-all">
                              Retake Week {currentWeekIndex} Quiz <i class="fa-solid fa-rotate-right ml-1"></i>
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 3.4 INTERACTIVE TEST BANK PAGE */}
              {currentStep === 'test_bank' && (
                <div class="max-w-6xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                    <h2 class="text-2xl font-bold text-slate-900">Interactive Subject Test Bank</h2>
                    <p class="text-xs text-slate-500 mt-1">Practice solving questions for your registered courses this semester to prepare for exams.</p>
                  </div>

                  {selectedCourses.length === 0 ? (
                    <div class="bg-white p-8 rounded-3xl border border-slate-200/80 shadow-md text-center space-y-4">
                      <div class="w-16 h-16 bg-burgundy-50 text-burgundy-600 rounded-2xl flex items-center justify-center mx-auto text-2xl">
                        <i class="fa-solid fa-clipboard-question"></i>
                      </div>
                      <p class="text-sm font-bold text-slate-700">You haven't selected any courses in the Planner yet.</p>
                      <button
                        onClick={() => setCurrentStep('planner')}
                        class="px-6 py-2.5 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-xs rounded-xl shadow-md transition-all">
                        Go to Course Planner
                      </button>
                    </div>
                  ) : (
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                      
                      <div class="md:col-span-1 space-y-3">
                        <h3 class="text-xs font-extrabold text-slate-400 uppercase tracking-wide px-1">Registered Courses</h3>
                        <div class="space-y-2">
                          {selectedCourses.map(course => {
                            const isSelected = activeTestBankCourseId === course.id;
                            const courseScore = calculateCourseScore(course.id);
                            return (
                              <button
                                key={course.id}
                                onClick={() => setActiveTestBankCourseId(course.id)}
                                class={`w-full p-4 rounded-xl border text-left transition-all ${
                                  isSelected 
                                    ? 'bg-burgundy-600 border-burgundy-600 text-white shadow-md' 
                                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                                }`}>
                                <p class="text-xs font-bold truncate">{course.name}</p>
                                <div class="flex justify-between items-center mt-2">
                                  <span class={`text-[10px] px-2 py-0.5 rounded font-bold ${
                                    isSelected ? 'bg-burgundy-700 text-burgundy-100' : 'bg-slate-100 text-slate-500'
                                  }`}>
                                    {course.credits} {course.credits === 1 ? 'Credit' : 'Credits'}
                                  </span>
                                  {courseScore !== null && (
                                    <span class={`text-[10px] font-bold ${isSelected ? 'text-white' : 'text-emerald-600'}`}>
                                      Score: {courseScore}%
                                    </span>
                                  )}
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      <div class="md:col-span-3">
                        {activeTestBankCourseId && (
                          <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-md space-y-6">
                            <div class="flex justify-between items-center border-b border-slate-100 pb-4">
                              <div>
                                <h3 class="font-extrabold text-lg text-slate-900">
                                  {selectedCourses.find(c => c.id === activeTestBankCourseId)?.name} Question Bank
                                </h3>
                                <p class="text-xs text-slate-400 font-semibold mt-0.5">Solve practice questions to test your understanding.</p>
                              </div>
                              <button
                                onClick={() => resetCourseQuiz(activeTestBankCourseId)}
                                class="px-3.5 py-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-burgundy-600 hover:border-burgundy-300 transition-all text-xs font-bold flex items-center gap-1">
                                <i class="fa-solid fa-rotate-right"></i>
                                <span>Reset Quiz</span>
                              </button>
                            </div>

                            <div class="space-y-8">
                              {(TEST_BANK_QUESTIONS[activeTestBankCourseId] || getFallbackQuestions(selectedCourses.find(c => c.id === activeTestBankCourseId)?.name || 'Course')).map((qObj, qIdx) => {
                                const userAns = testBankAnswers[activeTestBankCourseId]?.[qIdx];
                                const isAnswered = userAns !== undefined;

                                return (
                                  <div key={qIdx} class="space-y-3">
                                    <p class="text-sm font-bold text-slate-800">
                                      <span class="text-burgundy-600 mr-1">{qIdx + 1}.</span> {qObj.q}
                                    </p>
                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                      {qObj.options.map((option, optIdx) => {
                                        const isSelected = userAns === optIdx;
                                        const isCorrect = qObj.correct === optIdx;
                                        let btnStyle = "border-slate-200 hover:bg-slate-50 text-slate-700";

                                        if (isAnswered) {
                                          if (isCorrect) {
                                            btnStyle = "bg-emerald-50 border-emerald-500 text-emerald-800 shadow-sm";
                                          } else if (isSelected) {
                                            btnStyle = "bg-red-50 border-red-500 text-red-800 shadow-sm";
                                          } else {
                                            btnStyle = "border-slate-100 bg-slate-50 opacity-60 text-slate-400 cursor-not-allowed";
                                          }
                                        }

                                        return (
                                          <button
                                            key={optIdx}
                                            disabled={isAnswered}
                                            onClick={() => selectTestBankAnswer(activeTestBankCourseId, qIdx, optIdx)}
                                            class={`w-full p-4 rounded-xl border text-left text-xs font-semibold transition-all ${btnStyle}`}>
                                            <div class="flex items-center space-x-2">
                                              <span class={`w-5 h-5 rounded-full flex items-center justify-center border font-bold text-[10px] shrink-0 ${
                                                isAnswered && isCorrect ? 'bg-emerald-500 border-emerald-500 text-white' : 
                                                isAnswered && isSelected ? 'bg-red-500 border-red-500 text-white' :
                                                'border-slate-300 text-slate-500'
                                              }`}>
                                                {String.fromCharCode(65 + optIdx)}
                                              </span>
                                              <span>{option}</span>
                                            </div>
                                          </button>
                                        );
                                      })}
                                    </div>

                                    {isAnswered && (
                                      <div class={`p-4 rounded-xl text-xs font-semibold leading-relaxed border transition-all ${
                                        userAns === qObj.correct 
                                          ? 'bg-emerald-50/50 border-emerald-100 text-emerald-700' 
                                          : 'bg-amber-50/50 border-amber-100 text-amber-700'
                                      }`}>
                                        <div class="flex items-center gap-1.5 mb-1">
                                          <i class={userAns === qObj.correct ? "fa-solid fa-circle-check text-emerald-500" : "fa-solid fa-circle-exclamation text-amber-500"}></i>
                                          <span class="font-bold">{userAns === qObj.correct ? "Correct!" : "Incorrect"}</span>
                                        </div>
                                        {qObj.explanation}
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}
                      </div>

                    </div>
                  )}
                </div>
              )}

              {/* 4. TO-DO LIST PAGE */}
              {currentStep === 'todo' && (
                <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                    <div class="flex justify-between items-center mb-6">
                      <div>
                        <h2 class="text-2xl font-bold text-slate-900">Daily To-Do List</h2>
                        <p class="text-xs text-slate-500 mt-1">Manage academic and personal tasks</p>
                      </div>
                      <span class="px-3 py-1 rounded-full bg-burgundy-50 text-burgundy-700 text-xs font-bold border border-burgundy-100">
                        {tasks.filter(t => t.completed).length} / {tasks.length} Completed
                      </span>
                    </div>

                    <form onSubmit={handleAddTask} class="space-y-3 mb-6 p-4 bg-slate-50 rounded-2xl border border-slate-200/60">
                      <input 
                        type="text"
                        placeholder="What is the new task?"
                        value={newTaskTitle}
                        onChange={(e) => setNewTaskTitle(e.target.value)}
                        class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-burgundy-600 outline-none text-sm font-semibold bg-white"
                      />
                      <div class="flex flex-wrap gap-3 items-center justify-between">
                        <div class="flex space-x-2">
                          <select 
                            value={newTaskCategory}
                            onChange={(e) => setNewTaskCategory(e.target.value)}
                            class="px-3 py-2 rounded-lg border border-slate-300 text-xs font-semibold bg-white">
                            <option value="Academic">📚 Academic</option>
                            <option value="Projects">💼 Projects</option>
                            <option value="Personal">🏠 Personal</option>
                            <option value="Habits">🎯 Habits</option>
                          </select>

                          <select 
                            value={newTaskPriority}
                            onChange={(e) => setNewTaskPriority(e.target.value)}
                            class="px-3 py-2 rounded-lg border border-slate-300 text-xs font-semibold bg-white">
                            <option value="High">🔴 High Priority</option>
                            <option value="Medium">🟡 Medium Priority</option>
                            <option value="Low">🟢 Low Priority</option>
                          </select>
                        </div>

                        <button 
                          type="submit"
                          class="px-6 py-2 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-xs rounded-xl shadow-md">
                          + Add Task
                        </button>
                      </div>
                    </form>

                    <div class="space-y-3">
                      {tasks.map(task => (
                        <div 
                          key={task.id} 
                          class={`p-4 rounded-2xl border transition-all flex items-center justify-between ${
                            task.completed 
                            ? 'bg-slate-50/80 border-slate-200 opacity-60' 
                            : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                          }`}>
                          <div class="flex items-center space-x-3">
                            <button 
                              onClick={() => toggleTask(task.id)}
                              class={`w-6 h-6 rounded-lg border flex items-center justify-center transition-all ${
                                task.completed 
                                ? 'bg-emerald-500 border-emerald-500 text-white' 
                                : 'border-slate-300 bg-white hover:border-burgundy-600'
                              }`}>
                              {task.completed && <i class="fa-solid fa-check text-xs"></i>}
                            </button>
                            <div class="text-left">
                              <p class={`text-xs font-bold ${task.completed ? 'line-through text-slate-400' : 'text-slate-800'}`}>
                                {task.title}
                              </p>
                              <div class="flex space-x-2 mt-1">
                                <span class="text-[10px] font-semibold text-slate-400">Category: {task.category}</span>
                                <span class="text-[10px] font-semibold text-slate-400">|</span>
                                <span class={`text-[10px] font-bold ${task.priority === 'High' ? 'text-red-500' : task.priority === 'Medium' ? 'text-amber-500' : 'text-emerald-500'}`}>
                                  Priority: {task.priority}
                                </span>
                              </div>
                            </div>
                          </div>
                          <button 
                            onClick={() => deleteTask(task.id)}
                            class="text-slate-400 hover:text-red-600 p-1.5 transition-all">
                            <i class="fa-solid fa-trash-can text-xs"></i>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* 5. AI EMERGENCY PAGE */}
              {currentStep === 'emergency' && (
                <div class="max-w-2xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-8 rounded-3xl border border-slate-200/80 shadow-md">
                    <div class="flex items-center space-x-3 mb-6">
                      <div class="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-500 shadow-sm">
                        <i class="fa-solid fa-wand-magic-sparkles text-xl"></i>
                      </div>
                      <div>
                        <h2 class="text-2xl font-bold text-slate-900">AI Study Emergency Room</h2>
                        <p class="text-xs text-slate-500 mt-0.5">Generate a custom emergency compression study plan instantly</p>
                      </div>
                    </div>

                    <div class="space-y-4">
                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Situation / Reason</label>
                        <input 
                          type="text" required
                          value={emergencyReason}
                          onChange={(e) => setEmergencyReason(e.target.value)}
                          placeholder="Example: I have a midterm tomorrow and haven't studied at all"
                          class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-amber-500 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>

                      <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Available Study Hours</label>
                        <select 
                          value={availableHours}
                          onChange={(e) => setAvailableHours(e.target.value)}
                          class="w-full px-4 py-3 rounded-xl border border-amber-500 outline-none text-sm font-semibold bg-slate-50 focus:bg-white transition-all">
                          <option value="1">1 Hour</option>
                          <option value="2">2 Hours</option>
                          <option value="3">3 Hours</option>
                          <option value="4">4 Hours</option>
                          <option value="5">5+ Hours</option>
                        </select>
                      </div>

                      <button 
                        onClick={handleGenerateEmergencyPlan}
                        disabled={isGeneratingPlan || !emergencyReason.trim()}
                        class={`w-full py-3.5 text-white font-bold text-sm rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 ${
                          isGeneratingPlan || !emergencyReason.trim() 
                          ? 'bg-slate-300 cursor-not-allowed' 
                          : 'bg-amber-500 hover:bg-amber-600 shadow-amber-500/20'
                        }`}>
                        <i class="fa-solid fa-wand-magic-sparkles"></i>
                        <span>{isGeneratingPlan ? 'Generating Compression Plan...' : 'Generate Emergency Plan'}</span>
                      </button>
                    </div>
                  </div>

                  {aiEmergencyPlan && (
                    <div class="bg-white p-6 rounded-3xl border border-amber-200 bg-amber-50/20 shadow-lg space-y-4 animate-fade-in">
                      <div class="flex justify-between items-center">
                        <h3 class="font-extrabold text-slate-900 text-sm uppercase tracking-wide">🚨 Your Emergency Compression Study Plan</h3>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-700">AI Generated</span>
                      </div>
                      <p class="text-xs text-slate-700 font-bold">{aiEmergencyPlan.summary}</p>
                      <div class="space-y-2">
                        {aiEmergencyPlan.urgentTasks.map((t, idx) => (
                          <div key={idx} class="flex items-start gap-2.5 p-3 rounded-xl bg-white border border-slate-200/60 shadow-sm">
                            <span class="w-5 h-5 rounded-full bg-amber-100 text-amber-700 text-[10px] font-bold flex items-center justify-center shrink-0">{idx+1}</span>
                            <p class="text-xs text-slate-700 font-semibold mt-0.5 leading-relaxed">{t}</p>
                          </div>
                        ))}
                      </div>
                      <p class="text-xs text-amber-800 bg-amber-100/60 border border-amber-200/50 rounded-xl p-3 font-semibold">
                        💡 {aiEmergencyPlan.advice}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* 6. PROFILE PAGE */}
              {currentStep === 'profile' && (
                <div class="max-w-2xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-8 rounded-3xl border border-slate-200/80 shadow-md">
                    <div class="flex items-center space-x-4 mb-8">
                      <div class="w-16 h-16 rounded-3xl bg-burgundy-50 border border-burgundy-100 flex items-center justify-center text-burgundy-600 text-3xl shadow-md">
                        <i class="fa-solid fa-user-graduate"></i>
                      </div>
                      <div>
                        <h2 class="text-2xl font-bold text-slate-900">Student Academic Profile</h2>
                        <p class="text-xs text-slate-500 mt-0.5">View and edit your academic goals and details</p>
                      </div>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                      <div>
                        <span class="text-[11px] block font-bold text-slate-400 uppercase tracking-wide mb-1">Full Name</span>
                        <span class="text-sm font-bold text-slate-800">{student.fullName}</span>
                      </div>
                      <div>
                        <span class="text-[11px] block font-bold text-slate-400 uppercase tracking-wide mb-1">Student ID</span>
                        <span class="text-sm font-bold text-slate-800">{student.studentId}</span>
                      </div>
                      <div>
                        <span class="text-[11px] block font-bold text-slate-400 uppercase tracking-wide mb-1">University</span>
                        <span class="text-sm font-bold text-slate-800">{student.university}</span>
                      </div>
                      
                      <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-wide mb-1.5">Academic Major</label>
                        <select 
                          value={student.major}
                          onChange={(e) => {
                            const newMajor = e.target.value;
                            const majorCourses = IT_MAJORS[newMajor]?.courses || [];
                            const defaultSelection = majorCourses.slice(0, 3).map(c => c.id);
                            
                            handleUpdateProfile({
                              ...student,
                              major: newMajor,
                              targetGpa: roundVal(min(4.0, (parseFloat(student.gpa) || 3.0) + 0.2))
                            });
                            setSelectedCourseIds(defaultSelection);
                          }}
                          class="w-full px-3 py-1.5 rounded-lg border border-slate-300 outline-none text-xs font-semibold focus:border-burgundy-600 bg-white"
                        >
                          <option value="AIDS">Artificial Intelligence & Data Science (AIDS)</option>
                          <option value="CS">Computer Science (CS)</option>
                          <option value="CIS">Computer Information Systems (CIS)</option>
                          <option value="SWE">Software Engineering (SWE)</option>
                          <option value="BIT">Business Information Technology (BIT)</option>
                          <option value="CYS">Cyber Security (CYS)</option>
                        </select>
                      </div>

                      <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-wide mb-1.5">Cumulative GPA (Max 4.00)</label>
                        <input 
                          type="number" step="0.01" max="4.00" min="0.00"
                          value={student.gpa}
                          onChange={(e) => {
                            let val = parseFloat(e.target.value) || 0.0;
                            if (val > 4.0) val = 4.0;
                            if (val < 0.0) val = 0.0;
                            handleUpdateProfile({
                              ...student,
                              gpa: val.toString()
                            });
                          }}
                          class="w-full px-3 py-1.5 rounded-lg border border-slate-300 outline-none text-xs font-semibold focus:border-burgundy-600 bg-white"
                        />
                      </div>

                      <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-wide mb-1.5">Completed Credit Hours</label>
                        <input 
                          type="number" max="150" min="0"
                          value={student.completedHours}
                          onChange={(e) => {
                            let val = parseInt(e.target.value) || 0;
                            if (val > 150) val = 150;
                            if (val < 0) val = 0;
                            handleUpdateProfile({
                              ...student,
                              completedHours: val
                            });
                          }}
                          class="w-full px-3 py-1.5 rounded-lg border border-slate-300 outline-none text-xs font-semibold focus:border-burgundy-600 bg-white"
                        />
                      </div>

                      <div>
                        <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-wide mb-1.5">Target GPA (Max 4.00)</label>
                        <input 
                          type="number" step="0.01" max="4.00" min="0.00"
                          value={student.targetGpa}
                          onChange={(e) => {
                            let val = parseFloat(e.target.value) || 0.0;
                            if (val > 4.0) val = 4.0;
                            if (val < 0.0) val = 0.0;
                            handleUpdateProfile({
                              ...student,
                              targetGpa: val.toString()
                            });
                          }}
                          class="w-full px-3 py-1.5 rounded-lg border border-slate-300 outline-none text-xs font-semibold focus:border-burgundy-600 bg-white"
                        />
                        {isTargetGpaImpossible ? (
                          <p class="text-[10px] text-red-600 font-bold mt-1.5 flex items-center gap-1">
                            <i class="fa-solid fa-circle-xmark"></i>
                            <span>Impossible! Max you can reach is {maxGpaFormatted}</span>
                          </p>
                        ) : (
                          <p class="text-[10px] text-emerald-600 font-bold mt-1.5 flex items-center gap-1">
                            <i class="fa-solid fa-circle-check"></i>
                            <span>Achievable! Need to average {requiredGpaVal !== null ? requiredGpaVal.toFixed(2) : ''} in next {remainingHrsVal} hrs.</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 7. COURSE CHAPTERS PROGRESS PAGE */}
              {currentStep === 'chapters' && (
                <div class="max-w-6xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                    <h2 class="text-2xl font-bold text-slate-900">Course Chapters Progress</h2>
                    <p class="text-xs text-slate-500 mt-1">Check off each chapter as you finish it.</p>
                  </div>

                  {selectedCourses.length === 0 ? (
                    <div class="bg-white p-8 rounded-3xl border border-slate-200/80 shadow-md text-center space-y-4">
                      <div class="w-16 h-16 bg-burgundy-50 text-burgundy-600 rounded-2xl flex items-center justify-center mx-auto text-2xl">
                        <i class="fa-solid fa-layer-group"></i>
                      </div>
                      <p class="text-sm font-bold text-slate-700">You haven't selected any courses in the Planner yet.</p>
                      <button
                        onClick={() => setCurrentStep('planner')}
                        class="px-6 py-2.5 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-xs rounded-xl shadow-md transition-all">
                        Go to Course Planner
                      </button>
                    </div>
                  ) : (
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">

                      <div class="md:col-span-1 space-y-3">
                        <h3 class="text-xs font-extrabold text-slate-400 uppercase tracking-wide px-1">Registered Courses</h3>
                        <div class="space-y-2">
                          {selectedCourses.map(course => {
                            const isSelected = activeChaptersCourseId === course.id;
                            const percent = getCourseChapterPercent(course.id);
                            return (
                              <button
                                key={course.id}
                                onClick={() => setActiveChaptersCourseId(course.id)}
                                class={`w-full p-4 rounded-xl border text-left transition-all ${
                                  isSelected
                                    ? 'bg-burgundy-600 border-burgundy-600 text-white shadow-md'
                                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                                }`}>
                                <p class="text-xs font-bold truncate mb-2">{course.name}</p>
                                <div class={`w-full h-2.5 rounded-full overflow-hidden ${isSelected ? 'bg-burgundy-800/60' : 'bg-slate-100'}`}>
                                  <div
                                    class={`h-full rounded-full transition-all duration-500 ${isSelected ? 'bg-white' : percent === 100 ? 'bg-emerald-500' : 'bg-burgundy-600'}`}
                                    style={{ width: `${percent}%` }}>
                                  </div>
                                </div>
                                <p class={`text-[10px] font-bold mt-1.5 ${isSelected ? 'text-burgundy-100' : 'text-slate-400'}`}>{percent}% Complete</p>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      <div class="md:col-span-3">
                        {activeChaptersCourseId && (() => {
                          const activeCourse = selectedCourses.find(c => c.id === activeChaptersCourseId);
                          const percent = getCourseChapterPercent(activeChaptersCourseId);
                          const courseChaptersState = chapterProgress[activeChaptersCourseId] || {};
                          return (
                            <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-md space-y-6">
                              <div class="flex justify-between items-start border-b border-slate-100 pb-4 flex-wrap gap-3">
                                <div>
                                  <h3 class="font-extrabold text-lg text-slate-900">{activeCourse ? activeCourse.name : ''}</h3>
                                  <p class="text-xs text-slate-400 font-semibold mt-0.5">Mark each chapter as done to update progress.</p>
                                </div>
                                <button
                                  onClick={() => resetCourseChapters(activeChaptersCourseId)}
                                  class="px-3.5 py-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-burgundy-600 hover:border-burgundy-300 transition-all text-xs font-bold flex items-center gap-1">
                                  <i class="fa-solid fa-rotate-right"></i>
                                  <span>Reset Progress</span>
                                </button>
                              </div>

                              <div class="space-y-2">
                                <div class="flex justify-between items-center">
                                  <span class="text-xs font-bold text-slate-600">Overall Chapter Progress</span>
                                  <span class={`text-sm font-extrabold ${percent === 100 ? 'text-emerald-600' : 'text-burgundy-600'}`}>{percent}%</span>
                                </div>
                                <div class="w-full h-7 rounded-full bg-slate-100 border border-slate-200 overflow-hidden shadow-inner">
                                  <div
                                    class={`h-full rounded-full flex items-center justify-end px-3 transition-all duration-700 ease-out ${percent === 100 ? 'bg-gradient-to-r from-emerald-500 to-emerald-400' : 'bg-gradient-to-r from-burgundy-700 to-burgundy-500'}`}
                                    style={{ width: `${Math.max(percent, percent > 0 ? 10 : 0)}%` }}>
                                    {percent > 0 && (
                                      <span class="text-[10px] font-extrabold text-white drop-shadow">{percent}%</span>
                                    )}
                                  </div>
                                </div>
                                {percent === 100 && (
                                  <p class="text-xs font-bold text-emerald-600 flex items-center gap-1.5">
                                    <i class="fa-solid fa-circle-check"></i>
                                    <span>All chapters completed! Great work 🎉</span>
                                  </p>
                                )}
                              </div>

                              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {Array.from({ length: TOTAL_CHAPTERS }, (_, i) => i + 1).map(chapterNum => {
                                  const isDone = !!courseChaptersState[chapterNum];
                                  return (
                                    <button
                                      key={chapterNum}
                                      onClick={() => toggleChapter(activeChaptersCourseId, chapterNum)}
                                      class={`w-full p-4 rounded-xl border text-left transition-all flex items-center justify-between ${
                                        isDone
                                          ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                                          : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700'
                                      }`}>
                                      <span class="text-xs font-bold">Chapter {chapterNum}</span>
                                      <span class={`w-6 h-6 rounded-lg border flex items-center justify-center transition-all ${
                                        isDone
                                          ? 'bg-emerald-500 border-emerald-500 text-white'
                                          : 'border-slate-300 bg-white'
                                      }`}>
                                        {isDone && <i class="fa-solid fa-check text-xs"></i>}
                                      </span>
                                    </button>
                                  );
                                })}
                              </div>
                            </div>
                          );
                        })()}
                      </div>

                    </div>
                  )}
                </div>
              )}

              {/* 8. POMODORO TIMER PAGE */}
              {currentStep === 'pomodoro' && (
                <div class="max-w-2xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                    <h2 class="text-2xl font-bold text-slate-900">Pomodoro Study Timer</h2>
                    <p class="text-xs text-slate-500 mt-1">Focus in short bursts, then take a break.</p>
                  </div>

                  <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm">
                    <div class="grid grid-cols-3 gap-2 mb-4">
                      <button
                        onClick={() => applyPomodoroMode('25_5')}
                        class={`py-2.5 rounded-xl text-xs font-bold border transition-all ${pomodoroMode === '25_5' ? 'bg-burgundy-600 border-burgundy-600 text-white shadow-md' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'}`}>
                        25 / 5
                      </button>
                      <button
                        onClick={() => applyPomodoroMode('50_10')}
                        class={`py-2.5 rounded-xl text-xs font-bold border transition-all ${pomodoroMode === '50_10' ? 'bg-burgundy-600 border-burgundy-600 text-white shadow-md' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'}`}>
                        50 / 10
                      </button>
                      <button
                        onClick={() => applyPomodoroMode('custom')}
                        class={`py-2.5 rounded-xl text-xs font-bold border transition-all ${pomodoroMode === 'custom' ? 'bg-burgundy-600 border-burgundy-600 text-white shadow-md' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'}`}>
                        Custom
                      </button>
                    </div>

                    {pomodoroMode === 'custom' && (
                      <div class="flex items-end gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-200/60">
                        <div class="flex-1">
                          <label class="block text-[10px] font-bold text-slate-500 mb-1">Study (minutes)</label>
                          <input
                            type="number" min="1" max="180"
                            value={customStudyMin}
                            onChange={(e) => setCustomStudyMin(e.target.value)}
                            class="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-bold bg-white outline-none focus:border-burgundy-600" />
                        </div>
                        <div class="flex-1">
                          <label class="block text-[10px] font-bold text-slate-500 mb-1">Break (minutes)</label>
                          <input
                            type="number" min="1" max="60"
                            value={customBreakMin}
                            onChange={(e) => setCustomBreakMin(e.target.value)}
                            class="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-bold bg-white outline-none focus:border-burgundy-600" />
                        </div>
                        <button
                          onClick={applyCustomPomodoro}
                          class="px-4 py-2 bg-burgundy-600 hover:bg-burgundy-700 text-white text-xs font-bold rounded-lg shadow-md transition-all">
                          Apply
                        </button>
                      </div>
                    )}
                  </div>

                  <div class={`p-10 rounded-3xl border shadow-md text-center space-y-6 transition-all ${pomodoroPhase === 'study' ? 'bg-white border-slate-200/80' : 'bg-emerald-50 border-emerald-200'}`}>
                    <span class={`inline-block px-4 py-1.5 rounded-full text-xs font-extrabold uppercase tracking-wide ${pomodoroPhase === 'study' ? 'bg-burgundy-50 text-burgundy-700 border border-burgundy-100' : 'bg-emerald-100 text-emerald-700 border border-emerald-200'}`}>
                      {pomodoroPhase === 'study' ? '📚 Focus Time' : '☕ Break Time'}
                    </span>

                    <div class={`text-7xl font-extrabold tracking-tight ${pomodoroPhase === 'study' ? 'text-slate-900' : 'text-emerald-700'}`}>
                      {formatTime(pomodoroSecondsLeft)}
                    </div>

                    <div class="w-full h-4 rounded-full bg-slate-100 overflow-hidden max-w-md mx-auto">
                      <div
                        class={`h-full rounded-full transition-all duration-1000 ${pomodoroPhase === 'study' ? 'bg-burgundy-600' : 'bg-emerald-500'}`}
                        style={{ width: `${pomodoroProgressPercent}%` }}>
                      </div>
                    </div>

                    <div class="flex items-center justify-center gap-3">
                      <button
                        onClick={togglePomodoroRunning}
                        class={`px-8 py-3.5 rounded-2xl font-bold text-sm text-white shadow-lg transition-all flex items-center gap-2 ${pomodoroPhase === 'study' ? 'bg-burgundy-600 hover:bg-burgundy-700 shadow-burgundy-600/30' : 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-600/30'}`}>
                        <i class={`fa-solid ${pomodoroRunning ? 'fa-pause' : 'fa-play'}`}></i>
                        <span>{pomodoroRunning ? 'Pause' : 'Start'}</span>
                      </button>
                      <button onClick={resetPomodoro} class="px-5 py-3.5 rounded-2xl font-bold text-sm text-slate-600 bg-slate-100 hover:bg-slate-200 transition-all">
                        <i class="fa-solid fa-rotate-left"></i>
                      </button>
                      <button onClick={skipPomodoroPhase} class="px-5 py-3.5 rounded-2xl font-bold text-sm text-slate-600 bg-slate-100 hover:bg-slate-200 transition-all">
                        <i class="fa-solid fa-forward-step"></i>
                      </button>
                    </div>

                    <p class="text-xs font-bold text-slate-400">
                      Completed Study Sessions Today: <span class="text-burgundy-600">{pomodoroSessionsCompleted}</span>
                    </p>
                  </div>
                </div>
              )}

              {/* 9. EXAM CALENDAR PAGE */}
              {currentStep === 'exam_calendar' && (
                <div class="max-w-6xl mx-auto space-y-6 animate-fade-in">
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                    <h2 class="text-2xl font-bold text-slate-900">Exam Calendar</h2>
                    <p class="text-xs text-slate-500 mt-1">Track countdowns and manage exam halls.</p>
                  </div>

                  {nextExam ? (
                    <div class="bg-burgundy-600 p-6 sm:p-8 rounded-3xl shadow-lg text-white">
                      <div class="flex flex-wrap justify-between items-start gap-4">
                        <div>
                          <span class="text-[10px] font-bold uppercase tracking-wide bg-white/15 px-3 py-1 rounded-full">Next Exam</span>
                          <h3 class="text-xl font-extrabold mt-2">{nextExam.courseName}</h3>
                          <p class="text-xs font-semibold text-burgundy-100 mt-1">
                            <i class="fa-solid fa-calendar-day mr-1"></i> {nextExam.date} &nbsp;
                            <i class="fa-solid fa-clock ml-2 mr-1"></i> {nextExam.time} &nbsp;
                            <i class="fa-solid fa-location-dot ml-2 mr-1"></i> {nextExam.location}
                          </p>
                        </div>
                        {(() => {
                          const parts = getCountdownParts(nextExam.dt);
                          return (
                            <div class="flex gap-3">
                              {[['Days', parts.days], ['Hours', parts.hours], ['Min', parts.minutes], ['Sec', parts.seconds]].map(([label, val]) => (
                                <div key={label} class="bg-white/10 rounded-2xl px-3.5 py-2.5 text-center min-w-[60px]">
                                  <div class="text-2xl font-extrabold">{val.toString().padStart(2, '0')}</div>
                                  <div class="text-[9px] font-bold uppercase tracking-wide text-burgundy-100">{label}</div>
                                </div>
                              ))}
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                  ) : (
                    <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm text-center">
                      <p class="text-sm font-bold text-slate-500">No upcoming exams scheduled. Add one below!</p>
                    </div>
                  )}

                  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    <div class="lg:col-span-2 bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                      <div class="flex justify-between items-center mb-4">
                        <button onClick={() => changeCalendarMonth(-1)} class="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition-all">
                          <i class="fa-solid fa-chevron-left text-xs"></i>
                        </button>
                        <h3 class="font-extrabold text-slate-900 text-sm">{MONTH_NAMES[calendarViewDate.getMonth()]} {calendarViewDate.getFullYear()}</h3>
                        <button onClick={() => changeCalendarMonth(1)} class="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition-all">
                          <i class="fa-solid fa-chevron-right text-xs"></i>
                        </button>
                      </div>

                      <div class="grid grid-cols-7 gap-1.5 mb-2">
                        {WEEKDAY_NAMES.map(w => (
                          <div key={w} class="text-center text-[10px] font-bold text-slate-400 uppercase py-1">{w}</div>
                        ))}
                      </div>

                      <div class="grid grid-cols-7 gap-1.5">
                        {buildMonthGrid(calendarViewDate).map((day, idx) => {
                          const dayExams = examsOnDay(calendarViewDate, day);
                          const todayFlag = isToday(calendarViewDate, day);
                          return (
                            <div
                              key={idx}
                              onClick={() => day && setExamDraft({ ...examDraft, date: dateStrForDay(calendarViewDate, day) })}
                              class={`min-h-[64px] p-1.5 rounded-xl border text-left transition-all ${
                                !day ? 'border-transparent' :
                                dayExams.length > 0 ? 'bg-burgundy-50 border-burgundy-300 cursor-pointer hover:border-burgundy-500' :
                                'bg-slate-50 border-slate-100 hover:border-slate-300 cursor-pointer'
                              }`}>
                              {day && (
                                <>
                                  <span class={`text-[11px] font-bold ${todayFlag ? 'bg-burgundy-600 text-white px-1.5 py-0.5 rounded-md' : 'text-slate-600'}`}>{day}</span>
                                  {dayExams.slice(0, 2).map(ev => (
                                    <div key={ev.id} class="text-[8px] font-bold text-burgundy-700 bg-white/70 rounded px-1 mt-1 truncate">{ev.courseName}</div>
                                  ))}
                                </>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div class="space-y-6">
                      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-md">
                        <h3 class="font-extrabold text-sm text-slate-800 mb-3">Add Exam</h3>
                        <form onSubmit={handleAddExam} class="space-y-3">
                          <select
                            required
                            value={examDraft.courseId}
                            onChange={(e) => setExamDraft({ ...examDraft, courseId: e.target.value })}
                            class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold bg-slate-50 focus:bg-white outline-none focus:border-burgundy-600">
                            <option value="">Select Course...</option>
                            {selectedCourses.map(c => (
                              <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                          </select>
                          <input
                            type="date" required
                            value={examDraft.date}
                            onChange={(e) => setExamDraft({ ...examDraft, date: e.target.value })}
                            class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold bg-slate-50 focus:bg-white outline-none focus:border-burgundy-600" />
                          <input
                            type="time" required
                            value={examDraft.time}
                            onChange={(e) => setExamDraft({ ...examDraft, time: e.target.value })}
                            class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold bg-slate-50 focus:bg-white outline-none focus:border-burgundy-600" />
                          <input
                            type="text" placeholder="Exam Location / Hall"
                            value={examDraft.location}
                            onChange={(e) => setExamDraft({ ...examDraft, location: e.target.value })}
                            class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold bg-slate-50 focus:bg-white outline-none focus:border-burgundy-600" />
                          <button type="submit" class="w-full py-2.5 bg-burgundy-600 hover:bg-burgundy-700 text-white font-bold text-xs rounded-xl shadow-md transition-all">
                            + Add to Calendar
                          </button>
                        </form>
                      </div>

                      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-md">
                        <h3 class="font-extrabold text-sm text-slate-800 mb-3">Upcoming Exams</h3>
                        <div class="space-y-2 max-h-64 overflow-y-auto">
                          {upcomingExamsList.length === 0 && (
                            <p class="text-[11px] text-slate-400 font-semibold">No upcoming exams yet.</p>
                          )}
                          {upcomingExamsList.map(ev => (
                            <div key={ev.id} class="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center">
                              <div>
                                <p class="text-[11px] font-bold text-slate-800">{ev.courseName}</p>
                                <p class="text-[10px] text-slate-500 font-semibold">{ev.date} • {ev.time} • {ev.location}</p>
                              </div>
                              <button onClick={() => deleteExam(ev.id)} class="text-slate-400 hover:text-red-600 transition-all p-1">
                                <i class="fa-solid fa-trash-can text-xs"></i>
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* GPA CALCULATOR PAGE */}
              {currentStep === 'gpa' && (
                <div class="max-w-5xl mx-auto space-y-6 animate-fade-in">
                  
                  {/* Page Title */}
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
                    <h2 class="text-2xl font-bold text-slate-900">GPA Calculator & Tracker</h2>
                    <p class="text-xs text-slate-500 mt-1">Calculate your Semester and Cumulative GPA based on Hashemite University scale.</p>
                  </div>

                  {/* Previous GPA details */}
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
                    <h3 class="font-extrabold text-sm text-slate-800 border-b border-slate-100 pb-2">Previous Cumulative GPA (Optional)</h3>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Previous GPA</label>
                        <input
                          type="number" step="0.01" max="4.00" min="0.00"
                          placeholder="Previous GPA (e.g. 2.95)"
                          value={gpaPrev}
                          onChange={(e) => setGpaPrev(e.target.value)}
                          class="w-full px-4 py-2.5 rounded-xl border border-slate-300 outline-none text-xs font-semibold focus:border-burgundy-600 bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Previous Completed Hours</label>
                        <input
                          type="number" min="0" max="150"
                          placeholder="Previous Hours (e.g. 85)"
                          value={hoursPrev}
                          onChange={(e) => setHoursPrev(e.target.value)}
                          class="w-full px-4 py-2.5 rounded-xl border border-slate-300 outline-none text-xs font-semibold focus:border-burgundy-600 bg-slate-50 focus:bg-white transition-all"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Semester Courses Table */}
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4 overflow-x-auto">
                    <h3 class="font-extrabold text-sm text-slate-800 border-b border-slate-100 pb-2">Semester Courses</h3>
                    
                    <table class="w-full text-left border-collapse min-w-[600px]">
                      <thead>
                        <tr class="border-b border-slate-200 text-xs text-slate-400 font-bold">
                          <th class="pb-3 w-2/5 text-slate-500">Course Name</th>
                          <th class="pb-3 w-1/6 text-slate-500">Credits</th>
                          <th class="pb-3 w-1/6 text-slate-500">Grade</th>
                          <th class="pb-3 w-1/6 text-slate-500">Repeat?</th>
                          <th class="pb-3 w-1/6 text-slate-500">Prev Grade</th>
                          <th class="pb-3 w-12 text-center text-slate-500">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {gpaCourses.map((course, idx) => (
                          <tr key={course.id} class="border-b border-slate-100 text-xs font-semibold text-slate-700">
                            <td class="py-3 pr-2">
                              <input
                                type="text"
                                value={course.name}
                                onChange={(e) => {
                                  const updated = [...gpaCourses];
                                  updated[idx].name = e.target.value;
                                  setGpaCourses(updated);
                                }}
                                class="w-full px-3 py-2 rounded-lg border border-slate-200 outline-none focus:border-burgundy-500 text-xs"
                              />
                            </td>
                            <td class="py-3 pr-2">
                              <input
                                type="number" min="1" max="6"
                                value={course.credits}
                                onChange={(e) => {
                                  const updated = [...gpaCourses];
                                  updated[idx].credits = parseInt(e.target.value) || 0;
                                  setGpaCourses(updated);
                                }}
                                class="w-20 px-3 py-2 rounded-lg border border-slate-200 outline-none focus:border-burgundy-500 text-xs"
                              />
                            </td>
                            <td class="py-3 pr-2">
                              <select
                                value={course.grade}
                                onChange={(e) => {
                                  const updated = [...gpaCourses];
                                  updated[idx].grade = e.target.value;
                                  setGpaCourses(updated);
                                }}
                                class="px-3 py-2 rounded-lg border border-slate-200 outline-none focus:border-burgundy-500 text-xs bg-white"
                              >
                                <option value="">Grade...</option>
                                {Object.keys(GRADE_POINTS).map(g => (
                                  <option key={g} value={g}>{g}</option>
                                ))}
                              </select>
                            </td>
                            <td class="py-3 pr-2 text-center">
                              <input
                                type="checkbox"
                                checked={course.isRepeat}
                                onChange={(e) => {
                                  const updated = [...gpaCourses];
                                  updated[idx].isRepeat = e.target.checked;
                                  setGpaCourses(updated);
                                }}
                                class="w-4 h-4 text-burgundy-600 border-slate-300 rounded focus:ring-burgundy-500"
                              />
                            </td>
                            <td class="py-3 pr-2">
                              {course.isRepeat && (
                                <select
                                  value={course.prevGrade}
                                  onChange={(e) => {
                                    const updated = [...gpaCourses];
                                    updated[idx].prevGrade = e.target.value;
                                    setGpaCourses(updated);
                                  }}
                                  class="px-3 py-2 rounded-lg border border-slate-200 outline-none focus:border-burgundy-500 text-xs bg-white"
                                >
                                  <option value="">Prev...</option>
                                  {Object.keys(GRADE_POINTS).map(g => (
                                    <option key={g} value={g}>{g}</option>
                                  ))}
                                </select>
                              )}
                            </td>
                            <td class="py-3 text-center">
                              <button
                                onClick={() => {
                                  const updated = gpaCourses.filter((_, i) => i !== idx);
                                  setGpaCourses(updated);
                                }}
                                class="text-slate-400 hover:text-red-600 transition-all p-1"
                              >
                                <i class="fa-solid fa-trash-can text-sm"></i>
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    <div class="flex justify-between items-center pt-3">
                      <button
                        onClick={() => {
                          setGpaCourses([
                            ...gpaCourses,
                            { id: Date.now().toString(), name: `Course ${gpaCourses.length + 1}`, credits: 3, grade: '', isRepeat: false, prevGrade: '' }
                          ]);
                        }}
                        class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition-all"
                      >
                        + Add Course
                      </button>
                      <button
                        onClick={() => {
                          if (selectedCourses.length > 0) {
                            setGpaCourses(selectedCourses.map(c => ({
                              id: c.id,
                              name: c.name,
                              credits: c.credits,
                              grade: '',
                              isRepeat: false,
                              prevGrade: ''
                            })));
                          }
                        }}
                        class="px-4 py-2 border border-slate-200 text-slate-500 hover:text-burgundy-600 text-xs font-bold rounded-xl transition-all"
                      >
                        Reset to Planner Courses
                      </button>
                    </div>
                  </div>

                  {/* GPA Results Summary in Burgundy Color */}
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    {/* Semester GPA Card */}
                    <div class="bg-gradient-to-br from-burgundy-700 to-burgundy-900 p-8 rounded-3xl text-white shadow-xl flex flex-col justify-between">
                      <div>
                        <div class="flex justify-between items-center">
                          <span class="text-xs font-bold uppercase tracking-wider text-burgundy-200">Semester Status</span>
                          <span class="text-2xl font-bold bg-white/10 px-3 py-1 rounded-xl">
                            {gpaResults.semCreditsSum} Hrs
                          </span>
                        </div>
                        <h3 class="text-4xl font-extrabold tracking-tight mt-6">
                          {gpaResults.semesterGpa}
                        </h3>
                        <p class="text-xs text-burgundy-200 font-semibold mt-1">Semester GPA</p>
                      </div>
                      <div class="border-t border-white/10 pt-4 mt-6">
                        <div class="flex justify-between items-center">
                          <span class="text-xs font-bold text-burgundy-200">Rating</span>
                          <span class="text-sm font-extrabold">
                            {getGpaRating(gpaResults.semesterGpa)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Cumulative GPA Card */}
                    <div class="bg-gradient-to-br from-burgundy-800 to-burgundy-950 p-8 rounded-3xl text-white shadow-xl flex flex-col justify-between">
                      <div>
                        <div class="flex justify-between items-center">
                          <span class="text-xs font-bold uppercase tracking-wider text-burgundy-200">Cumulative Status</span>
                          <span class="text-2xl font-bold bg-white/10 px-3 py-1 rounded-xl">
                            {gpaResults.totalCumHours} Total Hrs
                          </span>
                        </div>
                        <h3 class="text-4xl font-extrabold tracking-tight mt-6">
                          {gpaResults.cumulativeGpa}
                        </h3>
                        <p class="text-xs text-burgundy-200 font-semibold mt-1">Cumulative GPA</p>
                      </div>
                      <div class="border-t border-white/10 pt-4 mt-6">
                        <div class="flex justify-between items-center">
                          <span class="text-xs font-bold text-burgundy-200">Rating</span>
                          <span class="text-sm font-extrabold">
                            {getGpaRating(gpaResults.cumulativeGpa)}
                          </span>
                        </div>
                      </div>
                    </div>

                  </div>

                </div>
              )}

              {/* 10. ADHKAR / DUAA PAGE (Arabic) */}
              {currentStep === 'adhkar' && (
                <div dir="rtl" class="max-w-3xl mx-auto space-y-6 animate-fade-in font-arabic">
                  <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md text-center">
                    <div class="w-14 h-14 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-3 text-2xl text-emerald-600">
                      <i class="fa-solid fa-hands-praying"></i>
                    </div>
                    <h2 class="text-2xl font-extrabold text-slate-900">أدعية قبل وبعد الدراسة</h2>
                    <p class="text-xs text-slate-500 mt-1">اللهم اجعل هذا العلم نافعاً لنا في الدنيا والآخرة</p>
                  </div>

                  <div class="bg-white p-6 sm:p-8 rounded-3xl border border-emerald-200 shadow-md">
                    <div class="flex items-center gap-2 mb-4">
                      <span class="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                        <i class="fa-solid fa-book-open"></i>
                      </span>
                      <h3 class="font-extrabold text-lg text-emerald-800">دعاء قبل الدراسة</h3>
                    </div>
                    <p class="text-sm leading-loose text-slate-700 font-medium">
                      اللهمّ إني أسألك فهم النبيين، وحفظ الملائكة المقربين، وأن تفتح عليّ بفضلك وكرمك فتوح العارفين، وأن تجعلني من عبادك العالمين. اللهمّ إني توكلت عليك، وسلمت أمري إليك، تولني بفضلك وافتح عليّ بقدرتك فتوح العارفين، وفهم النبيين، وحفظ الملائكة المكرمين. اللهمّ إني أسألك من العلم ما فيه خيري الدنيا والآخرة، اللهمّ فاجعل لي في كل حرف حسنة، وهوّن عليّ كل صعب، وذلل لي طريق العلم وحببني به. اللهمّ علّمني من كل خير، ويسّر لي أن أعمل بما علمتني، وتقبله مني، أنت حسبي ونعم الوكيل. اللهمّ إني أسألك من العلم أحسنه، ومن الفهم أكمله، ومن العمل أخلصه. اللهمّ إني أسألك علما نافعا، وقلبا خاشعا، وعملا صالحا متقبلا. اللهم بارك لي في العلم والفهم، وهوّن عليّ كل صعب، باسمك يا علّام الغيوب أبدأ؛ فباركني وبارك لي في الوقت والجهد.
                    </p>
                  </div>

                  <div class="bg-white p-6 sm:p-8 rounded-3xl border border-burgundy-200 shadow-md">
                    <div class="flex items-center gap-2 mb-4">
                      <span class="w-9 h-9 rounded-xl bg-burgundy-50 text-burgundy-700 flex items-center justify-center">
                        <i class="fa-solid fa-book"></i>
                      </span>
                      <h3 class="font-extrabold text-lg text-burgundy-800">دعاء بعد الدراسة</h3>
                    </div>
                    <p class="text-sm leading-loose text-slate-700 font-medium">
                      رَبِّ اشْرَحْ لِي صَدْرِي، وَيَسِّرْ لِي أَمْرِي، وَاحْلُلْ عُقْدَةً مِّن لِّسَانِي، يَفْقَهُوا قَوْلِي. اللهمّ إني أستودعك كلّ ما قرأته وكلّ ما حفظته وتعلمته، فأسألك أن تردّه إلَيَّ عند الحاجة له، فأنت القادر على كل شيء. اللهم يا رب العالمين، إنِّي توكلت عليك وسلمت أمري كلَّه إليك، لا ملجأ ولا منجى منك إلَّا إليك. اللهم لا سهْل إلَّا ما قد جعلته سهلًا، اللهم اجعل الصَّعب لي سهلًا. اللهم ذكّرني منه ما نسيتُ ولا حول ولا قوة إلا بالله العلي العظيم. اللهمّ إنّي أعوذ بك أن أضِلَّ أو أُضَلَّ في دراستي يا رب، أو أزِلّ أو أُزَلّ، أو أظلِمَ أو أُظلَم، أو أَجهَل أو يُجهَلَ عليّ.
                    </p>
                  </div>
                </div>
              )}

            </main>

            <footer class="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-400 font-semibold mt-8">
              <p>© 2026 EduPulse AI - Faculty of Information Technology, Hashemite University. All rights reserved.</p>
            </footer>

          </div>
        );
      }

      const container = document.getElementById('root');
      const root = ReactDOM.createRoot(container);
      root.render(<App />);