// Fasting Manager - Frontend Module
// Handles intermittent fasting functionality

class FastingManager {
    constructor(apiBaseUrl = '/api') {
        this.apiBaseUrl = apiBaseUrl;
        this.currentSession = null;
        this.updateInterval = null;
    }

    // Start a new fasting session
    async startFasting(fastingType = '16:8', notes = '') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fasting_type: fastingType,
                    notes: notes
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentSession = result.data;
                this.startUpdateTimer();
                this.showNotification('Fasting session started!', 'success');
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to start fasting');
            }
        } catch (error) {
            console.error('Start fasting error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    // End current fasting session
    async endFasting() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/end`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentSession = null;
                this.stopUpdateTimer();
                this.showNotification(`Fasting completed! Duration: ${result.data.duration_hours.toFixed(1)} hours`, 'success');
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to end fasting');
            }
        } catch (error) {
            console.error('End fasting error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    // Pause current fasting session
    async pauseFasting() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/pause`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentSession.status = 'paused';
                this.stopUpdateTimer();
                this.showNotification('Fasting session paused', 'info');
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to pause fasting');
            }
        } catch (error) {
            console.error('Pause fasting error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    // Resume paused fasting session
    async resumeFasting(sessionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/resume`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentSession.status = 'active';
                this.startUpdateTimer();
                this.showNotification('Fasting session resumed', 'success');
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to resume fasting');
            }
        } catch (error) {
            console.error('Resume fasting error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    // Cancel current fasting session
    async cancelFasting() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentSession = null;
                this.stopUpdateTimer();
                this.showNotification('Fasting session cancelled', 'info');
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to cancel fasting');
            }
        } catch (error) {
            console.error('Cancel fasting error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    // Get current fasting status
    async getFastingStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/status`);
            const result = await response.json();
            
            if (response.ok) {
                this.currentSession = result.data.active_session;
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to get fasting status');
            }
        } catch (error) {
            console.error('Get fasting status error:', error);
            throw error;
        }
    }

    // Get fasting sessions history
    async getFastingSessions(limit = 30) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/sessions?limit=${limit}`);
            const result = await response.json();
            
            if (response.ok) {
                return result.data.sessions;
            } else {
                throw new Error(result.message || 'Failed to get fasting sessions');
            }
        } catch (error) {
            console.error('Get fasting sessions error:', error);
            throw error;
        }
    }

    // Get fasting statistics
    async getFastingStats(days = 30) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/stats?days=${days}`);
            const result = await response.json();
            
            if (response.ok) {
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to get fasting stats');
            }
        } catch (error) {
            console.error('Get fasting stats error:', error);
            throw error;
        }
    }

    // Get fasting goals
    async getFastingGoals() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/goals`);
            const result = await response.json();
            
            if (response.ok) {
                return result.data.goals;
            } else {
                throw new Error(result.message || 'Failed to get fasting goals');
            }
        } catch (error) {
            console.error('Get fasting goals error:', error);
            throw error;
        }
    }

    // Create a new fasting goal
    async createFastingGoal(goalType, targetValue, periodStart, periodEnd) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/fasting/goals`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    goal_type: goalType,
                    target_value: targetValue,
                    period_start: periodStart,
                    period_end: periodEnd
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showNotification('Fasting goal created successfully!', 'success');
                return result.data;
            } else {
                throw new Error(result.message || 'Failed to create fasting goal');
            }
        } catch (error) {
            console.error('Create fasting goal error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }

    // Calculate current fasting duration
    calculateCurrentDuration(startTime) {
        if (!startTime) return 0;
        
        const start = new Date(startTime);
        const now = new Date();
        const diffMs = now - start;
        return diffMs / (1000 * 60 * 60); // Convert to hours
    }

    // Format duration in hours to human readable format
    formatDuration(hours) {
        if (hours < 1) {
            const minutes = Math.floor(hours * 60);
            const seconds = Math.floor((hours * 60 - minutes) * 60);
            return `${minutes}m ${seconds}s`;
        } else if (hours < 24) {
            const wholeHours = Math.floor(hours);
            const minutes = Math.floor((hours - wholeHours) * 60);
            const seconds = Math.floor(((hours - wholeHours) * 60 - minutes) * 60);
            return `${wholeHours}h ${minutes}m ${seconds}s`;
        } else {
            const days = Math.floor(hours / 24);
            const remainingHours = Math.floor(hours % 24);
            const minutes = Math.floor((hours % 24 - remainingHours) * 60);
            return `${days}d ${remainingHours}h ${minutes}m`;
        }
    }

    // Calculate countdown to fasting completion
    calculateCountdown(duration, fastingType) {
        const targets = {
            '16:8': 16,
            '18:6': 18,
            '20:4': 20,
            'OMAD': 23
        };
        
        const target = targets[fastingType];
        if (!target) return null;
        
        const remaining = target - duration;
        return remaining > 0 ? remaining : 0;
    }

    // Format countdown time
    formatCountdown(hours) {
        if (hours <= 0) {
            return 'Completed!';
        }
        
        const totalSeconds = Math.floor(hours * 3600);
        const remainingHours = Math.floor(totalSeconds / 3600);
        const remainingMinutes = Math.floor((totalSeconds % 3600) / 60);
        const remainingSeconds = totalSeconds % 60;
        
        if (remainingHours > 0) {
            return `${remainingHours}h ${remainingMinutes}m ${remainingSeconds}s`;
        } else if (remainingMinutes > 0) {
            return `${remainingMinutes}m ${remainingSeconds}s`;
        } else {
            return `${remainingSeconds}s`;
        }
    }

    // Get progress percentage for common fasting types
    getProgressPercentage(duration, fastingType) {
        const targets = {
            '16:8': 16,
            '18:6': 18,
            '20:4': 20,
            'OMAD': 23
        };
        
        const target = targets[fastingType];
        if (!target) return null;
        
        return Math.min(100, (duration / target) * 100);
    }

    // Start update timer for active sessions
    startUpdateTimer() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Update every second for real-time countdown
        this.updateInterval = setInterval(() => {
            this.updateFastingDisplay();
        }, 1000); // Update every second
    }

    // Stop update timer
    stopUpdateTimer() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    // Update fasting display
    updateFastingDisplay() {
        if (!this.currentSession || this.currentSession.status !== 'active') {
            return;
        }

        const duration = this.calculateCurrentDuration(this.currentSession.start_time);
        const formattedDuration = this.formatDuration(duration);
        const progress = this.getProgressPercentage(duration, this.currentSession.fasting_type);
        const countdown = this.calculateCountdown(duration, this.currentSession.fasting_type);
        const formattedCountdown = this.formatCountdown(countdown);

        // Update UI elements
        const durationElement = document.getElementById('fasting-duration');
        if (durationElement) {
            durationElement.textContent = formattedDuration;
        }

        // Update countdown display
        const countdownElement = document.getElementById('fasting-countdown');
        if (countdownElement) {
            countdownElement.textContent = formattedCountdown;
            
            // Add visual feedback for completion
            if (countdown <= 0) {
                countdownElement.classList.add('text-success', 'fw-bold');
                countdownElement.classList.remove('text-warning');
            } else if (countdown <= 1) {
                countdownElement.classList.add('text-warning', 'fw-bold');
                countdownElement.classList.remove('text-success');
            } else {
                countdownElement.classList.remove('text-success', 'text-warning', 'fw-bold');
            }
        }

        const progressElement = document.getElementById('fasting-progress');
        if (progressElement && progress !== null) {
            progressElement.style.width = `${progress}%`;
            progressElement.setAttribute('aria-valuenow', progress);
            
            // Change progress bar color based on completion
            if (progress >= 100) {
                progressElement.classList.remove('bg-primary');
                progressElement.classList.add('bg-success');
            } else if (progress >= 75) {
                progressElement.classList.remove('bg-primary', 'bg-success');
                progressElement.classList.add('bg-warning');
            } else {
                progressElement.classList.remove('bg-warning', 'bg-success');
                progressElement.classList.add('bg-primary');
            }
        }

        const progressTextElement = document.getElementById('fasting-progress-text');
        if (progressTextElement && progress !== null) {
            progressTextElement.textContent = `${Math.round(progress)}%`;
        }
    }

    // Show notification
    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            // Fallback to alert
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    // Initialize fasting manager
    async init() {
        try {
            const status = await this.getFastingStatus();
            
            if (status.is_fasting && status.active_session) {
                this.currentSession = status.active_session;
                this.startUpdateTimer();
            }
            
            return status;
        } catch (error) {
            console.error('Fasting manager init error:', error);
            return null;
        }
    }

    // Cleanup
    destroy() {
        this.stopUpdateTimer();
        this.currentSession = null;
    }
}

// Export for use in other modules
window.FastingManager = FastingManager;
