        // In-memory database simulation
        let workSessions = JSON.parse(localStorage.getItem('workSessions')) || [];
        let currentSession = null;
        let timerInterval = null;

        function updateCurrentTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent =
                now.toLocaleDateString() + ' - ' + now.toLocaleTimeString();
        }

        function formatTime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        function formatDuration(milliseconds) {
            const totalSeconds = Math.floor(milliseconds / 1000);
            const hours = Math.floor(totalSeconds / 3600);
            const minutes = Math.floor((totalSeconds % 3600) / 60);

            if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else {
                return `${minutes}m`;
            }
        }

        function startWork() {
            currentSession = {
                startTime: new Date(),
                endTime: null
            };

            // Update UI
            document.getElementById('startBtn').disabled = true;
            document.getElementById('startBtn').classList.add('btn-disabled');
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('stopBtn').classList.remove('btn-disabled');

            const timerDisplay = document.getElementById('timerDisplay');
            timerDisplay.classList.add('active');

            const statusIndicator = document.getElementById('statusIndicator');
            statusIndicator.innerHTML = '<span class="status-indicator status-working"></span><span>Working...</span>';

            // Start timer
            let startTime = currentSession.startTime.getTime();
            timerInterval = setInterval(() => {
                const elapsed = Math.floor((new Date().getTime() - startTime) / 1000);
                timerDisplay.textContent = formatTime(elapsed);
            }, 1000);
        }

        function stopWork() {
            if (!currentSession) return;

            currentSession.endTime = new Date();
            workSessions.push(currentSession);

            // Save to localStorage (simulating database)
            // Save to backend server (writes to sessions.json)
            fetch("http://localhost:3000/save", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(currentSession)
                }).then(res => res.json())
                .then(data => console.log(data))
                .catch(err => console.error("Save error:", err));

            // Clear timer
            clearInterval(timerInterval);

            // Update UI
            document.getElementById('startBtn').disabled = false;
            document.getElementById('startBtn').classList.remove('btn-disabled');
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('stopBtn').classList.add('btn-disabled');

            const timerDisplay = document.getElementById('timerDisplay');
            timerDisplay.classList.remove('active');
            timerDisplay.textContent = '00:00:00';

            const statusIndicator = document.getElementById('statusIndicator');
            statusIndicator.innerHTML = '<span class="status-indicator status-stopped"></span><span>Ready to work</span>';

            currentSession = null;
            updateStats();
            updateSessionsTable();
        }

        function updateStats() {
            const today = new Date().toDateString();
            const todaySessions = workSessions.filter(session =>
                session.startTime && new Date(session.startTime).toDateString() === today
            );

            let totalHours = 0;
            let totalMinutes = 0;

            todaySessions.forEach(session => {
                const start = new Date(session.startTime);
                const end = new Date(session.endTime);
                const duration = (end - start) / 1000 / 60; // in minutes
                totalMinutes += duration;
            });

            totalHours = Math.floor(totalMinutes / 60);
            const remainingMinutes = Math.floor(totalMinutes % 60);

            document.getElementById('todayHours').textContent =
                totalHours > 0 ? `${totalHours}h ${remainingMinutes}m` : `${remainingMinutes}m`;
            document.getElementById('sessionCount').textContent = todaySessions.length;

            const avgSession = todaySessions.length > 0 ? Math.floor(totalMinutes / todaySessions.length) : 0;
            document.getElementById('avgSession').textContent = `${avgSession}min`;
        }

        function updateSessionsTable() {
            const tableBody = document.getElementById('sessionsTable');

            if (workSessions.length === 0) {
                tableBody.innerHTML = `
                    <div class="table-row" style="text-align: center; color: #666; font-style: italic;">
                        <div style="grid-column: 1 / -1;">No sessions recorded yet</div>
                    </div>
                `;
                return;
            }

            tableBody.innerHTML = workSessions
                .slice(-10) // Show last 10 sessions
                .reverse()
                .map(session => {
                    const start = new Date(session.startTime);
                    const end = session.endTime ? new Date(session.endTime) : null;
                    const duration = end ? end - start : 0;

                    return `
                        <div class="table-row">
                            <div>${start.toLocaleDateString()}</div>
                            <div>${start.toLocaleTimeString()}</div>
                            <div>${end ? end.toLocaleTimeString() : 'In progress'}</div>
                            <div>${formatDuration(duration)}</div>
                        </div>
                    `;
                }).join('');
        }

        // Initialize
        updateCurrentTime();
        setInterval(updateCurrentTime, 1000);
        updateStats();
        updateSessionsTable();

        document.getElementById("startBtn").addEventListener("click", startWork);
        document.getElementById("stopBtn").addEventListener("click", stopWork);