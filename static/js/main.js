        let charts = {};

        // DOM Elements
        const analyzeForm = document.getElementById('analyzeForm');
        const resumeFileInput = document.getElementById('resumeFile');
        const jobDescription = document.getElementById('jobDescription');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const errorMessage = document.getElementById('errorMessage');
        const resultsSection = document.getElementById('resultsSection');
        const fileStatus = document.getElementById('fileStatus');
        const jdStatus = document.getElementById('jdStatus');
        const fileUploadLabel = document.getElementById('fileUploadLabel');
        const fileUploadWrapper = document.getElementById('fileUploadWrapper');
        const analyzeBtn = document.getElementById('analyzeBtn');

        // File upload handling
        resumeFileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            const fileNameDisplay = fileUploadLabel.querySelector('.file-name');
            
            if (file) {
                // Validate file type
                const allowedExtensions = ['pdf', 'doc', 'docx', 'txt'];
                const fileExtension = file.name.split('.').pop().toLowerCase();
                
                if (!allowedExtensions.includes(fileExtension)) {
                    showError('Please upload a PDF, DOC, DOCX, or TXT file');
                    resumeFileInput.value = '';
                    fileNameDisplay.textContent = 'Choose file or drag here';
                    fileUploadLabel.classList.remove('file-selected');
                    fileStatus.innerHTML = '';
                    return;
                }
                
                // Validate file size (5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showError('File size must be less than 5MB');
                    resumeFileInput.value = '';
                    fileNameDisplay.textContent = 'Choose file or drag here';
                    fileUploadLabel.classList.remove('file-selected');
                    fileStatus.innerHTML = '';
                    return;
                }
                
                // Update file name display
                fileNameDisplay.textContent = file.name;
                fileUploadLabel.classList.add('file-selected');
                fileStatus.innerHTML = `<span class="success"><i class="fas fa-check-circle"></i> ${file.name} selected (${(file.size / 1024).toFixed(1)} KB)</span>`;
                fileStatus.className = 'file-status success';
            } else {
                fileNameDisplay.textContent = 'Choose file or drag here';
                fileUploadLabel.classList.remove('file-selected');
                fileStatus.innerHTML = '';
            }
        });

        // Job description input handling
        jobDescription.addEventListener('input', (e) => {
            const length = e.target.value.length;
            
            if (length > 50) {
                jdStatus.innerHTML = `<i class="fas fa-check-circle"></i> JD received (${length} characters)`;
                jdStatus.className = 'jd-status success';
            } else {
                jdStatus.innerHTML = `<span style="color: #fbbf24;">${50 - length} more characters needed</span>`;
                jdStatus.className = 'jd-status';
            }
        });

        // Drag and drop handling
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadWrapper.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadWrapper.addEventListener(eventName, () => {
                fileUploadLabel.classList.add('dragging');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadWrapper.addEventListener(eventName, () => {
                fileUploadLabel.classList.remove('dragging');
            }, false);
        });

        fileUploadWrapper.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                // Create a new DataTransfer to set files
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(files[0]);
                resumeFileInput.files = dataTransfer.files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                resumeFileInput.dispatchEvent(event);
            }
        }, false);

        // Form submission
        analyzeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Validate inputs
            if (!resumeFileInput.files[0]) {
                showError('Please upload a resume file');
                return;
            }
            
            if (jobDescription.value.length < 50) {
                showError('Job description must be at least 50 characters');
                return;
            }
            
            // Prepare form data
            const formData = new FormData();
            formData.append('resume', resumeFileInput.files[0]);
            formData.append('job_description', jobDescription.value);
            
            // Show loading, hide error and results
            showLoading();
            hideError();
            hideResults();
            analyzeBtn.disabled = true;
            
            try {
                // Send request to Flask backend
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'An error occurred while analyzing the resume');
                }
                
                // Display results
                displayResults(data);
                
            } catch (error) {
                showError(error.message);
            } finally {
                hideLoading();
                analyzeBtn.disabled = false;
            }
        });

        // Display functions
        function showLoading() {
            loadingSpinner.style.display = 'block';
        }

        function hideLoading() {
            loadingSpinner.style.display = 'none';
        }

        function showError(message) {
            errorMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            errorMessage.style.display = 'block';
            setTimeout(() => hideError(), 5000);
        }

        function hideError() {
            errorMessage.style.display = 'none';
        }

        function hideResults() {
            resultsSection.style.display = 'none';
        }

        function showResults() {
            resultsSection.style.display = 'block';
            // Smooth scroll to results
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }

        // Display results
        function displayResults(data) {
            // Show results section
            showResults();
            
            // Display charts
            createGaugeChart(data.scores.overall_score);
            createBreakdownChart(data.scores);
            createSkillsChart(data.skills.matched_skills.length, data.skills.missing_skills.length);
            
            // Display metrics
            displayMetrics(data.scores, data.skills);
            
            // Display skills
            displaySkills(data.skills);
            
            // Display strengths
            displayStrengths(data.skills.strengths || []);
            
            // Display job roles
            displayJobRoles(data.predicted_roles || []);
            
            // Display skill suggestions
            displaySkillSuggestions(data.skills.suggestions || []);
            
            // Display detailed information
            displayDetails(data.resume_data || {}, data.jd_data || {});
            
            // Display recommendation
            displayRecommendation(data.recommendation || {}, data.skills.missing_skills.length);
        }

        // Create gauge chart for overall score
        function createGaugeChart(score) {
            const ctx = document.getElementById('gaugeChart').getContext('2d');
            
            // Destroy existing chart
            if (charts.gauge) charts.gauge.destroy();
            
            const color = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';
            
            charts.gauge = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [score, 100 - score],
                        backgroundColor: [color, '#e5e7eb'],
                        borderWidth: 0
                    }]
                },
                options: {
                    circumference: 180,
                    rotation: 270,
                    cutout: '75%',
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    }
                },
                plugins: [{
                    id: 'gaugeText',
                    afterDraw: (chart) => {
                        const { ctx, chartArea: { top, width, height } } = chart;
                        ctx.save();
                        ctx.font = 'bold 2.5em Poppins';
                        ctx.textAlign = 'center';
                        ctx.fillStyle = color;
                        ctx.fillText(`${score}%`, width / 2, top + height / 1.2);
                        ctx.font = '1em Poppins';
                        ctx.fillStyle = '#6b7280';
                        ctx.fillText('Match Score', width / 2, top + height / 1.2 + 30);
                        ctx.restore();
                    }
                }]
            });
        }

        // Create breakdown chart
        function createBreakdownChart(scores) {
            const ctx = document.getElementById('breakdownChart').getContext('2d');
            
            if (charts.breakdown) charts.breakdown.destroy();
            
            charts.breakdown = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Semantic Similarity', 'Skill Match'],
                    datasets: [{
                        label: 'Score (%)',
                        data: [scores.semantic_similarity || 0, scores.skill_match || 0],
                        backgroundColor: ['#667eea', '#764ba2'],
                        borderRadius: 8
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: 'rgba(0,0,0,0.05)' }
                        },
                        y: {
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        // Create skills pie chart
        function createSkillsChart(matched, missing) {
            const ctx = document.getElementById('skillsChart').getContext('2d');
            
            if (charts.skills) charts.skills.destroy();
            
            charts.skills = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Matched Skills', 'Missing Skills'],
                    datasets: [{
                        data: [matched, missing],
                        backgroundColor: ['#10b981', '#ef4444'],
                        borderWidth: 3,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }

        // Display metrics
        function displayMetrics(scores, skills) {
            const metricsGrid = document.getElementById('metricsGrid');
            const matchRate = scores.match_rate || 0;
            
            metricsGrid.innerHTML = `
                <div class="metric-card">
                    <div class="metric-label">Overall Match</div>
                    <div class="metric-value">${scores.overall_score || 0}%</div>
                    <div class="metric-delta ${scores.overall_score >= 70 ? 'positive' : 'negative'}">
                        ${scores.overall_score >= 70 ? '↑' : '↓'} ${((scores.overall_score || 0) - 70).toFixed(1)}% vs target
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Skills Found</div>
                    <div class="metric-value">${skills.resume_skills?.length || 0}</div>
                    <div class="metric-delta positive">
                        ✓ ${skills.matched_skills?.length || 0} matched
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Missing Skills</div>
                    <div class="metric-value">${skills.missing_skills?.length || 0}</div>
                    <div class="metric-delta ${skills.missing_skills?.length === 0 ? 'positive' : 'negative'}">
                        ${skills.missing_skills?.length === 0 ? '✓ All covered' : '⚠ Need to learn'}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Skill Match Rate</div>
                    <div class="metric-value">${matchRate.toFixed(1)}%</div>
                    <div class="metric-delta ${matchRate >= 60 ? 'positive' : 'negative'}">
                        ${matchRate >= 60 ? '↑' : '↓'} ${(matchRate - 60).toFixed(1)}% vs average
                    </div>
                </div>
            `;
        }

        // Display skills
        function displaySkills(skills) {
            const matchedSkills = document.getElementById('matchedSkills');
            const missingSkills = document.getElementById('missingSkills');
            
            if (skills.matched_skills && skills.matched_skills.length > 0) {
                matchedSkills.innerHTML = skills.matched_skills.map(skill => 
                    `<span class="skill-tag matched">${skill}</span>`
                ).join('');
            } else {
                matchedSkills.innerHTML = '<p class="no-data">No direct skill matches found</p>';
            }
            
            if (skills.missing_skills && skills.missing_skills.length > 0) {
                missingSkills.innerHTML = skills.missing_skills.map(skill => 
                    `<span class="skill-tag missing">${skill}</span>`
                ).join('');
            } else {
                missingSkills.innerHTML = '<p style="color: #10b981;">No missing skills! 🎉</p>';
            }
        }

        // Display strengths
        function displayStrengths(strengths) {
            const container = document.getElementById('strengthsContainer');
            
            if (strengths && strengths.length > 0) {
                container.innerHTML = strengths.map(skill => 
                    `<span class="skill-tag strength">${skill}</span>`
                ).join('');
            } else {
                container.innerHTML = '<p class="no-data">Build your skills to showcase your strengths!</p>';
            }
        }

        // Display job roles
        function displayJobRoles(roles) {
            const container = document.getElementById('rolesContainer');
            
            if (roles && roles.length > 0) {
                container.innerHTML = roles.map(role => `
                    <div class="role-card">
                        <div class="role-icon">🎯</div>
                        <div class="role-title">${role}</div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p class="no-data">No role predictions available</p>';
            }
        }

        // Display skill suggestions
        function displaySkillSuggestions(suggestions) {
            const container = document.getElementById('skillSuggestions');
            
            if (suggestions && suggestions.length > 0) {
                container.innerHTML = suggestions.map(skill => 
                    `<span class="skill-tag suggestion">${skill}</span>`
                ).join('');
            } else {
                container.innerHTML = '<p class="no-data">No suggestions at this time</p>';
            }
        }

        // Display detailed information
        function displayDetails(resumeData, jdData) {
            const resumeDetails = document.getElementById('resumeDetails');
            const jdDetails = document.getElementById('jdDetails');
            
            if (resumeData && Object.keys(resumeData).length > 0) {
                resumeDetails.innerHTML = `
                    <p><strong>Name:</strong> ${resumeData.name || 'N/A'}</p>
                    <p><strong>Email:</strong> ${resumeData.email || 'N/A'}</p>
                    <p><strong>Phone:</strong> ${resumeData.phone || 'N/A'}</p>
                    <p><strong>Experience:</strong> ${resumeData.experience || 'N/A'} years</p>
                    <p><strong>Education:</strong> ${resumeData.education ? resumeData.education.join(', ') : 'N/A'}</p>
                `;
            } else {
                resumeDetails.innerHTML = '<p class="no-data">Resume details not available</p>';
            }
            
            if (jdData && Object.keys(jdData).length > 0) {
                jdDetails.innerHTML = `
                    <p><strong>Job Title:</strong> ${jdData.job_title || 'N/A'}</p>
                    <p><strong>Seniority Level:</strong> ${jdData.seniority_level || 'N/A'}</p>
                    <p><strong>Experience Required:</strong> ${jdData.experience_required || 'N/A'}</p>
                    <p><strong>Skills Required:</strong> ${jdData.skills_count || 'N/A'} skills</p>
                `;
            } else {
                jdDetails.innerHTML = '<p class="no-data">Job description details not available</p>';
            }
        }

        // Display final recommendation
        function displayRecommendation(recommendation, missingSkillsCount) {
            const container = document.getElementById('finalRecommendation');
            
            const level = recommendation.level || 'needs-work';
            const message = recommendation.message || 'Analysis Complete';
            const advice = recommendation.advice || 'Review the results above to improve your resume.';
            
            let icon = '⚠️';
            if (level === 'excellent') icon = '🎉';
            else if (level === 'good') icon = '👍';
            
            let additionalAdvice = '';
            if (missingSkillsCount > 0) {
                additionalAdvice = `
                    <div class="skill-gap-analysis">
                        <p><strong>📚 Skill Gap Analysis:</strong></p>
                        <p>You're missing ${missingSkillsCount} key skills required for this role. 
                        Consider online courses, certifications, or hands-on projects to build these skills.</p>
                    </div>
                `;
            }
            
            container.className = `recommendation-box ${level}`;
            container.innerHTML = `
                <h3>${icon} ${message}</h3>
                <p>${advice}</p>
                ${additionalAdvice}
            `;
        }
    