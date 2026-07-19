// ============================================
// GRADWISE — APP LOGIC
// ============================================

// Auto-detect environment: use localhost for local development, or your deployed backend URL for production
const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : 'https://YOUR_BACKEND_URL_HERE'; // <-- You will change this when you get your Koyeb URL

const state = {
    token: localStorage.getItem('gw_token') || null,
    userId: localStorage.getItem('gw_user_id') || null,
    currentOrgId: null,
    currentOrgName: null,
    currentOrgRole: null
};

// ============================================
// DOM REFS & UTILS
// ============================================

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const views = {
    auth: $('#auth-view'),
    dashboard: $('#dashboard-view'),
    org: $('#org-view'),
    prog: $('#prog-view'),
    'faculty-dashboard': $('#faculty-dashboard-view'),
    'faculty-course-view': $('#faculty-course-view')
};

function showView(name) {
    Object.values(views).forEach(v => v.classList.remove('active'));
    views[name].classList.add('active');
}

function setLoading(btn, loading) {
    const label = btn.querySelector('span:first-child');
    const spinner = btn.querySelector('.spinner');
    if (!spinner) return;
    if (loading) {
        label.style.opacity = '0.5';
        spinner.classList.remove('hidden');
        btn.disabled = true;
    } else {
        label.style.opacity = '1';
        spinner.classList.add('hidden');
        btn.disabled = false;
    }
}

function toast(message, type = 'success') {
    const container = $('#toast-container');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

async function apiFetch(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(state.token ? { 'Authorization': `Bearer ${state.token}` } : {}),
        ...(options.headers || {}),
    };

    const res = await fetch(`${API}${endpoint}`, { ...options, headers });
    const data = await res.json();

    if (!res.ok) {
        let errMsg = data.detail || 'An error occurred';
        if (typeof errMsg === 'object') {
            errMsg = JSON.stringify(errMsg);
        }
        throw new Error(errMsg);
    }
    return data;
}

// ============================================
// AUTHENTICATION
// ============================================

function saveSession(token, userId) {
    state.token = token;
    state.userId = userId;
    localStorage.setItem('gw_token', token);
    localStorage.setItem('gw_user_id', userId);
}

function logout() {
    state.token = null;
    state.userId = null;
    localStorage.removeItem('gw_token');
    localStorage.removeItem('gw_user_id');
    $('#nav-right').innerHTML = '';
    showView('auth');
    toast('Logged out successfully', 'success');
}

function updateNavbar() {
    if (state.token) {
        $('#nav-right').innerHTML = `
            <span class="user-email">User ID: ${state.userId}</span>
            <button class="btn btn-outline" id="btn-logout" style="padding:4px 12px;font-size:12px;">Logout</button>
        `;
        $('#btn-logout').addEventListener('click', logout);
    } else {
        $('#nav-right').innerHTML = '';
    }
}

$$('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        $$('.auth-tab').forEach(t => t.classList.remove('active'));
        $$('.auth-form').forEach(f => f.classList.remove('active'));
        tab.classList.add('active');
        $(`#${tab.dataset.tab}-form`).classList.add('active');
    });
});

$('#login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#btn-login');
    const email = $('#login-email').value.trim();
    const password = $('#login-password').value;

    setLoading(btn, true);
    try {
        const data = await apiFetch('/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        saveSession(data.token, data.user_id);
        toast('Login successful', 'success');
        loadDashboard();
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

$('#signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#btn-signup');
    const email = $('#signup-email').value.trim();
    const password = $('#signup-password').value;

    setLoading(btn, true);
    try {
        const data = await apiFetch('/signup', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        toast(`Account created! User ID: ${data.user_id}. Please login.`, 'success');
        $('[data-tab="login"]').click();
        $('#login-email').value = email;
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

// ============================================
// DASHBOARD (ORGANIZATIONS)
// ============================================

async function loadDashboard() {
    updateNavbar();
    showView('dashboard');
    const grid = $('#org-grid');
    grid.innerHTML = '<p style="color:var(--text-secondary);padding:32px;">Loading organizations...</p>';

    try {
        const orgs = await apiFetch('/organizations');
        if (orgs.length === 0) {
            grid.innerHTML = '<p style="color:var(--text-secondary);padding:32px;">You haven\'t joined any organizations yet.</p>';
            return;
        }

        grid.innerHTML = '';
        orgs.forEach(org => {
            const card = document.createElement('div');
            card.className = 'org-card';
            card.innerHTML = `
                <div class="org-card-header">
                    <h3>${org.name}</h3>
                    <p>Org ID: ${org.organization_id}</p>
                </div>
                <div class="org-card-body">
                    <span class="role-tag">${org.role}</span>
                    <span style="font-size:12px;color:var(--text-secondary)">${org.status}</span>
                </div>
            `;
            card.addEventListener('click', () => openOrgView(org));
            grid.appendChild(card);
        });
    } catch (err) {
        grid.innerHTML = `<p style="color:var(--color-error);padding:32px;">Failed to load organizations.</p>`;
        toast(err.message, 'error');
    }
}

// ============================================
// MODALS
// ============================================

function openModal(id) { $(`#${id}`).classList.add('active'); }
function closeModal(id) { $(`#${id}`).classList.remove('active'); }

$$('.close-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.target.closest('.modal-overlay').classList.remove('active');
    });
});

$('#btn-open-join').addEventListener('click', () => openModal('join-org-modal'));
$('#btn-open-create').addEventListener('click', () => openModal('create-org-modal'));

$('#form-join-org').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#btn-submit-join');
    const invite_key = $('#join-invite-key').value.trim();

    setLoading(btn, true);
    try {
        await apiFetch('/membership', {
            method: 'POST',
            body: JSON.stringify({ user_id: parseInt(state.userId), invite_key }),
        });
        toast('Successfully joined organization!', 'success');
        closeModal('join-org-modal');
        $('#form-join-org').reset();
        loadDashboard();
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

$('#form-create-org').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#btn-submit-create');
    const name = $('#create-org-name').value.trim();

    setLoading(btn, true);
    try {
        const data = await apiFetch('/organizations', {
            method: 'POST',
            body: JSON.stringify({ name }),
        });
        toast(`Organization created! Invite key: ${data.invite_key}`, 'success');
        closeModal('create-org-modal');
        $('#form-create-org').reset();
        loadDashboard();
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

// ============================================
// ORGANIZATION VIEW
// ============================================

$('#btn-back-dashboard').addEventListener('click', loadDashboard);

async function openOrgView(org) {
    state.currentOrgId = org.organization_id;
    state.currentOrgName = org.name;
    state.currentOrgRole = org.role;
    state.currentOrgKey = org.invite_key;
    state.myContext = null;

    $('#org-title-display').textContent = org.name;
    $('#org-role-display').textContent = `Role: ${org.role}`;
    
    // Manage admin-only visibility
    $$('.admin-only').forEach(el => {
        el.style.display = (org.role === 'ADMIN') ? '' : 'none';
    });

    // Hide Course Catalog and Teaching tabs for students
    $$('.student-hidden').forEach(el => {
        el.style.display = (org.role === 'STUDENT') ? 'none' : '';
    });

    // Hide Course Catalog for faculty
    $$('.faculty-hidden').forEach(el => {
        if (org.role === 'FACULTY') el.style.display = 'none';
    });

    // Hide Attendance tab for admin
    $$('.admin-hidden').forEach(el => {
        if (org.role === 'ADMIN') el.style.display = 'none';
    });

    if (org.role !== 'ADMIN' && org.role !== 'PENDING') {
        try {
            state.myContext = await apiFetch(`/organization/${org.organization_id}/me/context`);
        } catch (e) {
            console.error("Failed to load context", e);
        }
    }

    if (org.role === 'FACULTY') {
        showView('faculty-dashboard');
        loadFacultyDashboard(org);
        return;
    }

    // Default to the first tab
    $$('.org-nav-tab')[0].click();
    showView('org');
    
    loadDepartmentsAndPrograms();
}

$$('.org-nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        $$('.org-nav-tab').forEach(t => t.classList.remove('active'));
        $$('.org-tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        
        const tabName = tab.dataset.orgTab;
        $(`#tab-${tabName}`).classList.add('active');

        if (tabName === 'academic') loadDepartmentsAndPrograms();
        else if (tabName === 'catalog') loadCourseCatalog();
        else if (tabName === 'people') loadPeople();
        else if (tabName === 'teaching') loadTeaching();
        else if (tabName === 'attendance') loadAttendance();
        else if (tabName === 'assessments') loadAssessments();
        // Add more loaders here as needed
    });
});

async function loadPeople() {
    const list = $('#people-list');
    list.innerHTML = '<p class="empty-state">Loading people...</p>';

    // Update header based on role
    const peopleHeader = $('#people-header');
    if (state.myContext && state.myContext.role === 'STUDENT') {
        peopleHeader.textContent = 'My Faculty';
    } else {
        peopleHeader.textContent = 'Students & Faculty';
    }

    try {
        // Student-specific people view: show only faculty from their enrolled courses
        if (state.myContext && state.myContext.role === 'STUDENT') {
            const enrollments = await apiFetch(`/students/${state.myContext.user_id}/enrollments?org_id=${state.currentOrgId}`);
            
            if (enrollments.length === 0) {
                list.innerHTML = '<p class="empty-state">No faculty to show — you are not enrolled in any courses yet.</p>';
                return;
            }

            // Deduplicate faculty by user_id, and track which courses they teach
            const facultyMap = {};
            enrollments.forEach(e => {
                if (!facultyMap[e.faculty_user_id]) {
                    facultyMap[e.faculty_user_id] = {
                        faculty_user_id: e.faculty_user_id,
                        faculty_email: e.faculty_email,
                        courses: []
                    };
                }
                facultyMap[e.faculty_user_id].courses.push(`${e.course_code}: ${e.course_name}`);
            });

            let html = '<div style="display:flex; flex-direction:column; gap:12px;">';
            Object.values(facultyMap).forEach(fac => {
                html += `
                    <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid var(--border-color);">
                        <div style="display:flex; justify-content: space-between; align-items:center;">
                            <div>
                                <h4 style="color:var(--primary); margin:0;">${fac.faculty_email}</h4>
                                <p style="margin:4px 0 0 0; font-size:14px; color:var(--text-secondary);">Faculty ID: ${fac.faculty_user_id}</p>
                            </div>
                            <span style="background: var(--bg-color); padding: 4px 12px; border-radius: 16px; font-size:12px; font-weight:500;">FACULTY</span>
                        </div>
                        <div style="margin-top:8px; padding-top:8px; border-top:1px solid var(--border-color);">
                            <p style="font-size:13px; color:var(--text-secondary); margin:0;">Teaches:</p>
                            ${fac.courses.map(c => `<span style="display:inline-block; background:var(--bg-color); padding:2px 8px; border-radius:4px; font-size:12px; margin:4px 4px 0 0;">${c}</span>`).join('')}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            list.innerHTML = html;
            return;
        }

        // Faculty-specific people view: show only their students
        if (state.myContext && state.myContext.role === 'FACULTY') {
            peopleHeader.textContent = 'My Students';
            // 1. Fetch all periods
            const periods = await apiFetch(`/organization/${state.currentOrgId}/periods`);
            let myOfferings = [];
            
            // 2. Fetch offerings for all periods
            for (const p of periods) {
                const offerings = await apiFetch(`/organization/${state.currentOrgId}/offerings?period_id=${p.period_id}&org_id=${state.currentOrgId}`);
                myOfferings.push(...offerings.filter(o => o.faculty_user_id === state.myContext.user_id));
            }

            if (myOfferings.length === 0) {
                list.innerHTML = '<p class="empty-state">No students to show — you are not teaching any courses yet.</p>';
                return;
            }

            // 3. Fetch enrollments for all my offerings
            const studentMap = {};
            for (const off of myOfferings) {
                const enrollments = await apiFetch(`/offerings/${off.offering_id}/enrollments`);
                enrollments.forEach(e => {
                    if (!studentMap[e.student_user_id]) {
                        studentMap[e.student_user_id] = {
                            student_user_id: e.student_user_id,
                            email: e.email,
                            roll_no: e.roll_no,
                            courses: []
                        };
                    }
                    if (!studentMap[e.student_user_id].courses.includes(off.course_name)) {
                        studentMap[e.student_user_id].courses.push(off.course_name);
                    }
                });
            }

            if (Object.keys(studentMap).length === 0) {
                list.innerHTML = '<p class="empty-state">No students are enrolled in your courses.</p>';
                return;
            }

            let html = '<div style="display:flex; flex-direction:column; gap:12px;">';
            Object.values(studentMap).forEach(stu => {
                html += `
                    <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid var(--border-color);">
                        <div style="display:flex; justify-content: space-between; align-items:center;">
                            <div>
                                <h4 style="color:var(--primary); margin:0;">${stu.email}</h4>
                                <p style="margin:4px 0 0 0; font-size:14px; color:var(--text-secondary);">Roll No: ${stu.roll_no}</p>
                            </div>
                            <span style="background: var(--bg-color); padding: 4px 12px; border-radius: 16px; font-size:12px; font-weight:500;">STUDENT</span>
                        </div>
                        <div style="margin-top:8px; padding-top:8px; border-top:1px solid var(--border-color);">
                            <p style="font-size:13px; color:var(--text-secondary); margin:0;">Enrolled in:</p>
                            ${stu.courses.map(c => `<span style="display:inline-block; background:var(--bg-color); padding:2px 8px; border-radius:4px; font-size:12px; margin:4px 4px 0 0;">${c}</span>`).join('')}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            list.innerHTML = html;
            return;
        }

        let people = await apiFetch(`/organization/${state.currentOrgId}/membership`);
        
        if (state.currentOrgRole !== 'ADMIN') {
            people = people.filter(p => p.role === 'ADMIN' || p.role === 'FACULTY');
        }

        if (people.length === 0) {
            list.innerHTML = '<p class="empty-state">No people found.</p>';
            return;
        }
        let html = '<div style="display:flex; flex-direction:column; gap:12px;">';
        people.forEach(p => {
            let roleDisplay = `<span style="background: var(--bg-color); padding: 4px 12px; border-radius: 16px; font-size:12px; font-weight:500;">${p.role}</span>`;
            
            if (state.currentOrgRole === 'ADMIN' && p.user_id !== parseInt(state.userId)) {
                roleDisplay = `
                    <select class="form-control role-select" data-user-id="${p.user_id}" style="padding: 4px 8px; width: auto; display: inline-block;">
                        <option value="PENDING" ${p.role === 'PENDING' ? 'selected' : ''}>PENDING</option>
                        <option value="STUDENT" ${p.role === 'STUDENT' ? 'selected' : ''}>STUDENT</option>
                        <option value="FACULTY" ${p.role === 'FACULTY' ? 'selected' : ''}>FACULTY</option>
                        <option value="ADMIN" ${p.role === 'ADMIN' ? 'selected' : ''}>ADMIN</option>
                    </select>
                `;
            }

            html += `
                <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid var(--border-color); display:flex; justify-content: space-between; align-items:center;">
                    <div>
                        <h4 style="color:var(--primary); margin:0;">User ID: ${p.user_id}</h4>
                        <p style="margin:4px 0 0 0; font-size:14px; color:var(--text-secondary);">Status: ${p.status}</p>
                    </div>
                    <div>
                        ${roleDisplay}
                    </div>
                </div>
            `;
        });
        html += '</div>';
        list.innerHTML = html;

        $$('.role-select').forEach(select => {
            select.addEventListener('change', async (e) => {
                const userId = parseInt(e.target.dataset.userId);
                const newRole = e.target.value;
                try {
                    await apiFetch(`/organization/${state.currentOrgId}/membership`, {
                        method: 'PATCH',
                        body: JSON.stringify({ user_id: userId, role: newRole })
                    });
                    toast('Role updated successfully!', 'success');
                    loadPeople();
                } catch (err) {
                    toast(err.message, 'error');
                    loadPeople(); 
                }
            });
        });

        // Populate student registration dropdowns
        const uidSelect = $('#student-uid');
        uidSelect.innerHTML = '<option value="" disabled selected>Select User (Pending)</option>';
        people.filter(p => p.role === 'PENDING').forEach(p => {
            uidSelect.innerHTML += `<option value="${p.user_id}">User ID: ${p.user_id}</option>`;
        });

        const progSelect = $('#student-prog');
        progSelect.innerHTML = '<option value="" disabled selected>Loading programs...</option>';
        apiFetch(`/organization/${state.currentOrgId}/programs`)
            .then(progs => {
                progSelect.innerHTML = '<option value="" disabled selected>Select Program</option>';
                progs.forEach(p => {
                    progSelect.innerHTML += `<option value="${p.program_id}">${p.name}</option>`;
                });
            })
            .catch(err => {});

        // Populate faculty registration dropdowns
        const facUidSelect = $('#fac-uid');
        facUidSelect.innerHTML = '<option value="" disabled selected>Select User (Pending/Faculty)</option>';
        people.filter(p => p.role === 'PENDING' || p.role === 'FACULTY').forEach(p => {
            facUidSelect.innerHTML += `<option value="${p.user_id}">User ID: ${p.user_id} (${p.role})</option>`;
        });

        const facDeptSelect = $('#fac-dept');
        facDeptSelect.innerHTML = '<option value="" disabled selected>Loading departments...</option>';
        apiFetch(`/organization/${state.currentOrgId}/departments`)
            .then(depts => {
                facDeptSelect.innerHTML = '<option value="" disabled selected>Select Department</option>';
                depts.forEach(d => {
                    facDeptSelect.innerHTML += `<option value="${d.department_id}">${d.name}</option>`;
                });
            })
            .catch(err => {});

    } catch(err) {
        list.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

async function loadTeaching() {
    const periodSelect = $('#teaching-period-select');
    
    // 1. Fetch periods and populate period dropdown
    periodSelect.innerHTML = '<option value="" disabled selected>Loading periods...</option>';
    try {
        const periods = await apiFetch(`/organization/${state.currentOrgId}/periods?org_id=${state.currentOrgId}`);
        periodSelect.innerHTML = '<option value="" disabled selected>Select Academic Period</option>';
        periods.forEach(p => {
            periodSelect.innerHTML += `<option value="${p.period_id}">${p.label} (Sem ${p.semester_number})</option>`;
        });
    } catch (err) {
        periodSelect.innerHTML = '<option value="" disabled selected>Error loading periods</option>';
    }

    // 2. Populate Course dropdown for Create Offering
    const courseSelect = $('#off-course');
    courseSelect.innerHTML = '<option value="" disabled selected>Loading courses...</option>';
    apiFetch(`/organization/${state.currentOrgId}/courses?org_id=${state.currentOrgId}`)
        .then(courses => {
            courseSelect.innerHTML = '<option value="" disabled selected>Select Course</option>';
            courses.forEach(c => {
                courseSelect.innerHTML += `<option value="${c.course_id}">${c.course_code} - ${c.course_name}</option>`;
            });
        }).catch(e => { courseSelect.innerHTML = '<option value="" disabled selected>Error</option>'; });

    // 3. Populate Faculty & Student dropdowns
    const facultySelect = $('#off-faculty');
    const studentSelect = $('#enr-student');
    facultySelect.innerHTML = '<option value="" disabled selected>Loading faculty...</option>';
    studentSelect.innerHTML = '<option value="" disabled selected>Loading students...</option>';
    
    apiFetch(`/organization/${state.currentOrgId}/membership?org_id=${state.currentOrgId}`)
        .then(members => {
            facultySelect.innerHTML = '<option value="" disabled selected>Select Faculty</option>';
            members.filter(m => m.role === 'FACULTY' || m.role === 'ADMIN').forEach(m => {
                facultySelect.innerHTML += `<option value="${m.user_id}">User ID: ${m.user_id} (${m.role})</option>`;
            });

            studentSelect.innerHTML = '<option value="" disabled selected>Select Student</option>';
            members.filter(m => m.role === 'STUDENT').forEach(m => {
                studentSelect.innerHTML += `<option value="${m.user_id}">User ID: ${m.user_id}</option>`;
            });
        }).catch(e => { 
            facultySelect.innerHTML = '<option value="" disabled selected>Error</option>';
            studentSelect.innerHTML = '<option value="" disabled selected>Error</option>';
        });

    // Add change listener for period select
    periodSelect.addEventListener('change', (e) => {
        loadOfferings(e.target.value);
    });
}

async function loadOfferings(periodId) {
    const list = $('#offerings-list');
    const enrOfferingSelect = $('#enr-offering');
    
    list.innerHTML = '<p class="empty-state">Loading offerings...</p>';
    enrOfferingSelect.innerHTML = '<option value="" disabled selected>Loading offerings...</option>';
    
    try {
        let offerings = await apiFetch(`/organization/${state.currentOrgId}/offerings?period_id=${periodId}&org_id=${state.currentOrgId}`);
        
        if (state.myContext) {
            if (state.myContext.role === 'FACULTY') {
                offerings = offerings.filter(o => o.faculty_user_id === state.myContext.user_id);
            } else if (state.myContext.role === 'STUDENT') {
                const myEnrollments = await apiFetch(`/students/${state.myContext.user_id}/enrollments?org_id=${state.currentOrgId}`);
                const enrolledOfferingIds = myEnrollments.map(e => e.offering_id);
                offerings = offerings.filter(o => enrolledOfferingIds.includes(o.offering_id));
            }
        }

        if (offerings.length === 0) {
            list.innerHTML = '<p class="empty-state">No offerings available in this period.</p>';
            enrOfferingSelect.innerHTML = '<option value="" disabled selected>No Offerings</option>';
            return;
        }
        
        enrOfferingSelect.innerHTML = '<option value="" disabled selected>Select Offering</option>';
        let html = '<div style="display:flex; flex-direction:column; gap:12px;">';
        
        offerings.forEach(off => {
            enrOfferingSelect.innerHTML += `<option value="${off.offering_id}">${off.course_code} - ${off.course_name} (Sec ${off.section})</option>`;
            
            html += `
                <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="color:var(--primary); margin:0;">${off.course_code}: ${off.course_name}</h4>
                        <p style="margin:4px 0 0 0; font-size:14px; color:var(--text-secondary);">Section: ${off.section} • Credits: ${off.credits}</p>
                        <p style="margin:4px 0 0 0; font-size:14px; color:var(--text-secondary);">Faculty ID: ${off.faculty_user_id}</p>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        list.innerHTML = html;
        
    } catch(err) {
        list.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
        enrOfferingSelect.innerHTML = '<option value="" disabled selected>Error loading</option>';
    }
}

async function loadCourseCatalog() {
    const list = $('#catalog-list');
    list.innerHTML = '<p class="empty-state">Loading catalog...</p>';
    try {
        let courses;
        if (state.myContext && state.myContext.role === 'STUDENT') {
            if (state.myContext.program_id) {
                courses = await apiFetch(`/programs/${state.myContext.program_id}/courses?org_id=${state.currentOrgId}`);
            } else {
                list.innerHTML = '<p class="empty-state">You don\'t have any courses yet.</p>';
                return;
            }
        } else {
            courses = await apiFetch(`/organization/${state.currentOrgId}/courses?org_id=${state.currentOrgId}`);
        }
        
        if (courses.length === 0) {
            list.innerHTML = '<p class="empty-state">No courses in the catalog yet.</p>';
            return;
        }
        let html = '<div class="prog-grid">';
        courses.forEach(c => {
            html += `
                <div class="prog-card" style="cursor:default;">
                    <div>
                        <h4 style="color:var(--primary)">${c.course_code}</h4>
                        <p style="font-size:14px; color:var(--text-primary); margin-top:4px">${c.course_name}</p>
                        <p style="margin-top:8px">Credits: ${c.credits}</p>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        list.innerHTML = html;
    } catch(err) {
        list.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

async function loadDepartmentsAndPrograms() {
    const container = $('#dept-boards-container');
    container.innerHTML = '<p class="empty-state">Loading academic structure...</p>';

    try {
        let [depts, progs] = await Promise.all([
            apiFetch(`/organization/${state.currentOrgId}/departments`),
            apiFetch(`/organization/${state.currentOrgId}/programs`)
        ]);

        if (state.myContext) {
            if (state.myContext.role === 'STUDENT') {
                depts = depts.filter(d => d.department_id === state.myContext.department_id);
                progs = progs.filter(p => p.program_id === state.myContext.program_id);
            } else if (state.myContext.role === 'FACULTY') {
                depts = depts.filter(d => d.department_id === state.myContext.department_id);
            }
        }

        if (depts.length === 0) {
            container.innerHTML = '<p class="empty-state">No departments available.</p>';
            return;
        }

        container.innerHTML = '';
        
        depts.forEach(dept => {
            const board = document.createElement('div');
            board.className = 'dept-board';
            
            const deptProgs = progs.filter(p => String(p.department_name) === String(dept.name));
            
            let progHtml = '';
            deptProgs.forEach(p => {
                progHtml += `
                    <div class="prog-card" data-prog-id="${p.program_id}" data-prog-name="${p.name}">
                        <div>
                            <h4>${p.name}</h4>
                            <p>${p.level} • ${p.duration_years} Years</p>
                        </div>
                    </div>
                `;
            });
            
            if (state.currentOrgRole === 'ADMIN') {
                progHtml += `<button class="btn-add-prog" data-dept-id="${dept.department_id}">+</button>`;
            }

            board.innerHTML = `
                <div class="dept-board-header">
                    <h2>${dept.name} <span style="color:var(--text-secondary);font-size:14px;font-weight:400">(${dept.code})</span></h2>
                </div>
                <div class="prog-grid">
                    ${progHtml}
                </div>
            `;
            container.appendChild(board);
        });

        // Add event listeners for + buttons
        $$('.btn-add-prog').forEach(btn => {
            btn.addEventListener('click', (e) => {
                $('#prog-dept-id').value = e.target.dataset.deptId;
                openModal('create-prog-modal');
            });
        });

        // Add event listeners for Program cards to drill down
        $$('.prog-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const progId = e.currentTarget.dataset.progId;
                const progName = e.currentTarget.dataset.progName;
                openProgramView(progId, progName);
            });
        });

    } catch (err) {
        container.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

$('#btn-back-org').addEventListener('click', () => {
    showView('org');
});

$('#btn-copy-code').addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(state.currentOrgKey);
        toast('Organization code copied to clipboard!', 'success');
    } catch (err) {
        toast('Failed to copy code.', 'error');
    }
});

function openProgramView(progId, progName) {
    state.currentProgId = progId;
    $('#prog-title-display').textContent = progName;
    showView('prog');

    // Update header based on role
    const header = $('#prog-courses-header');
    if (state.myContext && state.myContext.role === 'STUDENT') {
        header.textContent = 'My Enrolled Courses';
    } else {
        header.textContent = 'Mapped Courses';
    }

    loadMappedCourses();
    
    // Only populate course mapping dropdown for admins
    if (state.currentOrgRole === 'ADMIN') {
        const select = $('#map-course-id');
        select.innerHTML = '<option value="" disabled selected>Loading courses...</option>';
        apiFetch(`/organization/${state.currentOrgId}/courses`)
            .then(courses => {
                select.innerHTML = '<option value="" disabled selected>Select Course</option>';
                courses.forEach(c => {
                    select.innerHTML += `<option value="${c.course_id}">${c.course_code} - ${c.course_name}</option>`;
                });
            })
            .catch(err => {
                select.innerHTML = '<option value="" disabled selected>Error loading</option>';
            });
    }
}

async function loadMappedCourses() {
    const list = $('#mapped-courses-list');
    list.innerHTML = '<p class="empty-state">Loading courses...</p>';
    try {
        // Student view: show only enrolled courses with faculty info
        if (state.myContext && state.myContext.role === 'STUDENT') {
            const enrollments = await apiFetch(`/students/${state.myContext.user_id}/enrollments?org_id=${state.currentOrgId}`);
            
            if (enrollments.length === 0) {
                list.innerHTML = '<p class="empty-state">You are not enrolled in any courses yet.</p>';
                return;
            }
            
            let html = '';
            enrollments.forEach(e => {
                html += `
                    <div class="offering-item">
                        <h4>${e.course_name} (${e.course_code})</h4>
                        <div class="offering-meta">
                            <span>Credits: ${e.credits}</span>
                            <span>Section: ${e.section}</span>
                            <span>Period: ${e.period_label}</span>
                        </div>
                        <div class="offering-meta" style="margin-top:4px;">
                            <span>Faculty: ${e.faculty_email}</span>
                            <span>Status: ${e.status}</span>
                        </div>
                    </div>
                `;
            });
            list.innerHTML = html;
            return;
        }

        // Faculty view: show only courses they teach in this program
        if (state.myContext && state.myContext.role === 'FACULTY') {
            const mappedCourses = await apiFetch(`/programs/${state.currentProgId}/courses?org_id=${state.currentOrgId}`);
            const mappedCourseIds = mappedCourses.map(c => c.course_id);

            const periods = await apiFetch(`/organization/${state.currentOrgId}/periods`);
            let myOfferings = [];
            
            for (const p of periods) {
                const offerings = await apiFetch(`/organization/${state.currentOrgId}/offerings?period_id=${p.period_id}&org_id=${state.currentOrgId}`);
                myOfferings.push(...offerings.filter(o => o.faculty_user_id === state.myContext.user_id && mappedCourseIds.includes(o.course_id)));
            }

            if (myOfferings.length === 0) {
                list.innerHTML = '<p class="empty-state">You do not have any offerings in this program.</p>';
                return;
            }

            let html = '';
            myOfferings.forEach(o => {
                html += `
                    <div class="offering-item">
                        <h4>${o.course_name} (${o.course_code})</h4>
                        <div class="offering-meta">
                            <span>Credits: ${o.credits}</span>
                            <span>Section: ${o.section}</span>
                        </div>
                    </div>
                `;
            });
            list.innerHTML = html;
            return;
        }

        // Admin view: show all mapped courses
        const courses = await apiFetch(`/programs/${state.currentProgId}/courses?org_id=${state.currentOrgId}`);
        if (courses.length === 0) {
            list.innerHTML = '<p class="empty-state">No courses mapped to this program.</p>';
            return;
        }
        
        let html = '';
        courses.forEach(c => {
            html += `
                <div class="offering-item">
                    <h4>${c.course_name} (${c.course_code})</h4>
                    <div class="offering-meta">
                        <span>Credits: ${c.credits}</span>
                        <span>Semester: ${c.semester}</span>
                        <span>Type: ${c.is_core ? 'Core' : 'Elective'}</span>
                    </div>
                </div>
            `;
        });
        list.innerHTML = html;
    } catch(err) {
        list.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

$('#form-create-prog').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#btn-submit-prog');
    
    setLoading(btn, true);
    try {
        await apiFetch(`/organization/${state.currentOrgId}/programs`, {
            method: 'POST',
            body: JSON.stringify({
                department_id: parseInt($('#prog-dept-id').value),
                name: $('#prog-name').value,
                level: $('#prog-level').value,
                duration_years: parseInt($('#prog-duration').value)
            }),
        });
        toast('Program created!', 'success');
        closeModal('create-prog-modal');
        $('#form-create-prog').reset();
        loadDepartmentsAndPrograms();
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

$$('.sidebar-header').forEach(header => {
    header.addEventListener('click', () => {
        header.parentElement.classList.toggle('open');
    });
});

// SIDEBAR FORMS
async function handleSidebarSubmit(formId, btnId, endpoint, buildPayload, onSuccess = null) {
    $(formId).addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = $(btnId);
        setLoading(btn, true);
        try {
            await apiFetch(endpoint(), {
                method: 'POST',
                body: JSON.stringify(buildPayload()),
            });
            toast('Operation successful!', 'success');
            $(formId).reset();
            if (onSuccess) onSuccess();
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            setLoading(btn, false);
        }
    });
}

handleSidebarSubmit('#form-dept', '#btn-dept', 
    () => `/organization/${state.currentOrgId}/departments`,
    () => ({
        name: $('#dept-name').value,
        code: $('#dept-code').value
    }),
    loadDepartmentsAndPrograms
);

handleSidebarSubmit('#form-course', '#btn-course', 
    () => `/organization/${state.currentOrgId}/courses`,
    () => ({
        course_code: $('#course-code').value,
        course_name: $('#course-name').value,
        credits: parseInt($('#course-credits').value)
    }),
    loadCourseCatalog
);

$('#form-map-course').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#btn-map-course');
    const programId = state.currentProgId;
    setLoading(btn, true);
    try {
        await apiFetch(`/programs/${programId}/courses?org_id=${state.currentOrgId}`, {
            method: 'POST',
            body: JSON.stringify({
                course_id: parseInt($('#map-course-id').value),
                semester: parseInt($('#map-semester').value),
                is_core: $('#map-is-core').checked
            }),
        });
        toast('Course successfully linked to Program!', 'success');
        $('#form-map-course').reset();
        loadMappedCourses();
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

// People Tab Handlers
handleSidebarSubmit('#form-student', '#btn-student', 
    () => `/organization/${state.currentOrgId}/students?org_id=${state.currentOrgId}`,
    () => ({
        user_id: parseInt($('#student-uid').value),
        program_id: parseInt($('#student-prog').value),
        roll_no: $('#student-roll').value,
        admission_year: parseInt($('#student-year').value)
    })
);

handleSidebarSubmit('#form-faculty', '#btn-faculty', 
    () => `/organization/${state.currentOrgId}/faculty?org_id=${state.currentOrgId}`,
    () => ({
        user_id: parseInt($('#fac-uid').value),
        department_id: parseInt($('#fac-dept').value),
        employee_code: $('#fac-emp-code').value,
        designation: $('#fac-designation').value,
        joining_date: $('#fac-join-date').value
    })
);

// Teaching Tab Handlers
handleSidebarSubmit('#form-period', '#btn-period', 
    () => `/organization/${state.currentOrgId}/periods?org_id=${state.currentOrgId}`,
    () => ({
        label: $('#period-label').value,
        semester_number: parseInt($('#period-sem').value),
        academic_year: parseInt($('#period-year').value),
        start_date: $('#period-start').value,
        end_date: $('#period-end').value
    }),
    () => { loadTeaching(); } // Reload to update period dropdown
);

$('#form-offering').addEventListener('submit', async (e) => {
    e.preventDefault();
    const periodId = $('#teaching-period-select').value;
    if (!periodId) {
        toast('Please select an Academic Period first', 'error');
        return;
    }
    const btn = $('#btn-offering');
    setLoading(btn, true);
    try {
        await apiFetch(`/organization/${state.currentOrgId}/offerings?org_id=${state.currentOrgId}`, {
            method: 'POST',
            body: JSON.stringify({
                period_id: parseInt(periodId),
                course_id: parseInt($('#off-course').value),
                faculty_user_id: parseInt($('#off-faculty').value),
                section: $('#off-section').value
            })
        });
        toast('Offering created successfully!', 'success');
        $('#form-offering').reset();
        loadOfferings(periodId);
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

$('#form-enroll').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = $('#btn-enroll');
    const offeringId = parseInt($('#enr-offering').value);
    setLoading(btn, true);
    try {
        await apiFetch(`/offerings/${offeringId}/enrollments?org_id=${state.currentOrgId}`, {
            method: 'POST',
            body: JSON.stringify({
                student_user_id: parseInt($('#enr-student').value)
            })
        });
        toast('Student enrolled successfully!', 'success');
        $('#form-enroll').reset();
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

// ============================================
// ATTENDANCE
// ============================================

let currentAttendanceSessionId = null;

async function loadAttendance() {
    if (!state.myContext) return;

    if (state.myContext.role === 'STUDENT') {
        $('#student-attendance-view').style.display = 'block';

        
        const list = $('#student-attendance-list');
        list.innerHTML = '<p class="empty-state">Loading your attendance...</p>';
        
        try {
            const enrollments = await apiFetch(`/students/${state.myContext.user_id}/enrollments?org_id=${state.currentOrgId}`);
            if (enrollments.length === 0) {
                list.innerHTML = '<p class="empty-state">You are not enrolled in any courses.</p>';
                return;
            }

            let html = `
                <table class="data-table" style="width:100%; border-collapse:collapse; margin-top:16px;">
                    <thead>
                        <tr style="border-bottom: 2px solid var(--border-color); text-align:left;">
                            <th style="padding:12px;">Course</th>
                            <th style="padding:12px;">Sessions</th>
                            <th style="padding:12px;">Present</th>
                            <th style="padding:12px;">Late</th>
                            <th style="padding:12px;">Absent</th>
                            <th style="padding:12px;">Excused</th>
                            <th style="padding:12px;">Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            for (const e of enrollments) {
                const report = await apiFetch(`/students/${state.myContext.user_id}/attendance/${e.offering_id}`);
                const color = report.attendance_percentage >= 75 ? 'var(--success)' : 'var(--error)';
                html += `
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <td style="padding:12px;">${e.course_code}: ${e.course_name}</td>
                        <td style="padding:12px;">${report.total_sessions}</td>
                        <td style="padding:12px;">${report.present}</td>
                        <td style="padding:12px;">${report.late}</td>
                        <td style="padding:12px;">${report.absent}</td>
                        <td style="padding:12px;">${report.excused}</td>
                        <td style="padding:12px; font-weight:bold; color:${color};">${report.attendance_percentage}%</td>
                    </tr>
                `;
            }

            html += '</tbody></table>';
            list.innerHTML = html;
        } catch (err) {
            list.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
        }
    }
}

async function loadAssessments() {
    if (!state.myContext) return;

    if (state.myContext.role === 'STUDENT') {
        $('#student-assessments-view').style.display = 'block';

        const list = $('#student-assessments-list');
        list.innerHTML = '<p class="empty-state">Loading your scores...</p>';

        try {
            const enrollments = await apiFetch(`/students/${state.myContext.user_id}/enrollments?org_id=${state.currentOrgId}`);
            if (enrollments.length === 0) {
                list.innerHTML = '<p class="empty-state">You are not enrolled in any courses.</p>';
                return;
            }

            let html = '';
            
            for (const e of enrollments) {
                const performance = await apiFetch(`/students/${state.myContext.user_id}/performance/${e.offering_id}`);
                
                html += `
                    <div class="card" style="margin-bottom: 16px;">
                        <h4 style="margin-top:0; color:var(--primary);">${e.course_code}: ${e.course_name}</h4>
                        <p style="font-size:13px; color:var(--text-secondary); margin-bottom: 12px;">Total Course Score: ${performance.total_weighted_score.toFixed(2)} / ${performance.weightage_covered.toFixed(2)}</p>
                        
                        <table class="data-table" style="width:100%; border-collapse:collapse;">
                            <thead>
                                <tr style="border-bottom: 2px solid var(--border-color); text-align:left;">
                                    <th style="padding:8px;">Assessment</th>
                                    <th style="padding:8px;">Type</th>
                                    <th style="padding:8px;">Max Marks</th>
                                    <th style="padding:8px;">Weightage</th>
                                    <th style="padding:8px;">My Marks</th>
                                    <th style="padding:8px;">Percentage</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                if (performance.scores.length === 0) {
                    html += `<tr><td colspan="6" style="padding:8px; text-align:center; color:var(--text-secondary);">No assessments graded yet.</td></tr>`;
                } else {
                    performance.scores.forEach(s => {
                        html += `
                            <tr style="border-bottom: 1px solid var(--border-color);">
                                <td style="padding:8px;">${s.title || '-'}</td>
                                <td style="padding:8px;">${s.type}</td>
                                <td style="padding:8px;">${s.max_marks}</td>
                                <td style="padding:8px;">${s.weightage}%</td>
                                <td style="padding:8px; font-weight:bold;">${s.marks !== null ? s.marks : '-'}</td>
                                <td style="padding:8px;">${s.percentage !== null ? s.percentage.toFixed(1) + '%' : '-'}</td>
                            </tr>
                        `;
                    });
                }
                html += '</tbody></table></div>';
            }
            list.innerHTML = html;
        } catch (err) {
            list.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
        }
    }
}

// ============================================
// FACULTY UI (ISOLATED)
// ============================================

$('#btn-back-faculty-dash').addEventListener('click', loadDashboard);
$('#btn-back-faculty-course').addEventListener('click', () => showView('faculty-dashboard'));

async function loadFacultyDashboard(org) {
    $('#faculty-org-title').textContent = org.name;
    const periodSelect = $('#faculty-period-select');
    periodSelect.innerHTML = '<option value="" disabled selected>Loading periods...</option>';
    
    try {
        const periods = await apiFetch(`/organization/${state.currentOrgId}/periods?org_id=${state.currentOrgId}`);
        periodSelect.innerHTML = '<option value="" disabled selected>Select Academic Period</option>';
        periods.forEach(p => {
            periodSelect.innerHTML += `<option value="${p.period_id}">${p.label} (Sem ${p.semester_number})</option>`;
        });
    } catch (err) {
        periodSelect.innerHTML = '<option value="" disabled selected>Error loading periods</option>';
    }

    // Remove old listeners to avoid duplicates
    const newSelect = periodSelect.cloneNode(true);
    periodSelect.parentNode.replaceChild(newSelect, periodSelect);

    newSelect.addEventListener('change', async (e) => {
        const periodId = e.target.value;
        const grid = $('#faculty-offerings-grid');
        grid.innerHTML = '<p class="empty-state">Loading your classes...</p>';

        try {
            let offerings = await apiFetch(`/organization/${state.currentOrgId}/offerings?period_id=${periodId}&org_id=${state.currentOrgId}`);
            // Strictly filter to the logged-in faculty
            offerings = offerings.filter(o => o.faculty_user_id === state.myContext.user_id);

            if (offerings.length === 0) {
                grid.innerHTML = '<p class="empty-state">You are not teaching any classes in this period.</p>';
                return;
            }

            let html = '';
            offerings.forEach(off => {
                html += `
                    <div class="prog-card" style="cursor:pointer;" onclick="openFacultyCourse(${off.offering_id}, '${off.course_code}', '${off.course_name}', '${off.section}')">
                        <div>
                            <h4 style="color:var(--primary); margin-bottom: 4px;">${off.course_code}</h4>
                            <p style="font-weight: 500; font-size: 15px;">${off.course_name}</p>
                            <p style="font-size: 13px; color: var(--text-secondary); margin-top: 8px;">Section: ${off.section}</p>
                        </div>
                    </div>
                `;
            });
            grid.innerHTML = html;
        } catch (err) {
            grid.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
        }
    });
}

// Faculty Course View Tab Navigation
$$('#faculty-course-view .course-nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Deactivate all tabs and contents
        $$('#faculty-course-view .course-nav-tab').forEach(t => t.classList.remove('active'));
        $$('#faculty-course-view .course-tab-content').forEach(c => c.style.display = 'none');
        
        // Activate clicked
        tab.classList.add('active');
        const targetId = tab.dataset.target;
        document.getElementById(targetId).style.display = 'block';

        // Load specific tab data if necessary
        if (targetId === 'course-attendance-tab') {
            loadCourseAttendance(state.currentOfferingId);
        } else if (targetId === 'course-assessments-tab') {
            loadCourseAssessments(state.currentOfferingId);
        }
    });
});

async function openFacultyCourse(offeringId, courseCode, courseName, section) {
    state.currentOfferingId = offeringId;
    $('#faculty-course-title').textContent = `${courseCode}: ${courseName}`;
    $('#faculty-course-section').textContent = `Section ${section}`;
    
    // Reset to Roster tab by default
    $$('#faculty-course-view .course-nav-tab').forEach(t => t.classList.remove('active'));
    $$('#faculty-course-view .course-tab-content').forEach(c => c.style.display = 'none');
    $('#faculty-course-view .course-nav-tab[data-target="course-roster-tab"]').classList.add('active');
    document.getElementById('course-roster-tab').style.display = 'block';

    showView('faculty-course-view');
    await renderCourseRoster(offeringId);
}

// ----------------------------------------
// FACULTY COURSE: ATTENDANCE
// ----------------------------------------
let fcCurrentSessionId = null;

async function loadCourseAttendance(offeringId) {
    const list = $('#fc-sessions-list');
    const markingContainer = $('#fc-attendance-marking-container');
    
    markingContainer.style.display = 'none';
    list.innerHTML = '<p class="empty-state">Loading sessions...</p>';

    try {
        const sessions = await apiFetch(`/offerings/${offeringId}/sessions`);
        if (sessions.length === 0) {
            list.innerHTML = '<p class="empty-state">No sessions created yet.</p>';
            return;
        }

        list.innerHTML = '';
        sessions.forEach(s => {
            const btn = document.createElement('button');
            btn.className = 'btn';
            btn.style.cssText = 'background: white; border: 1px solid var(--border-color); color: var(--text-color); white-space: nowrap; padding: 6px 12px;';
            btn.textContent = `${s.session_date} ${s.topic ? `(${s.topic})` : ''}`;
            btn.onclick = () => loadFcAttendanceRoster(offeringId, s);
            list.appendChild(btn);
        });
    } catch (err) {
        list.innerHTML = `<p style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

async function loadFcAttendanceRoster(offeringId, session) {
    fcCurrentSessionId = session.session_id;
    const markingContainer = $('#fc-attendance-marking-container');
    const roster = $('#fc-attendance-roster');
    
    markingContainer.style.display = 'block';
    $('#fc-current-session-label').textContent = `Session: ${session.session_date} ${session.topic ? `(${session.topic})` : ''}`;
    roster.innerHTML = '<p>Loading roster...</p>';

    try {
        const [enrollments, attendance] = await Promise.all([
            apiFetch(`/offerings/${offeringId}/enrollments`),
            apiFetch(`/sessions/${session.session_id}/attendance`)
        ]);

        if (enrollments.length === 0) {
            roster.innerHTML = '<p class="empty-state">No students enrolled in this offering.</p>';
            return;
        }

        const attMap = {};
        attendance.forEach(a => attMap[a.student_user_id] = a.status);

        let html = `
            <table class="data-table" style="width:100%; border-collapse:collapse; background: white;">
                <thead>
                    <tr style="border-bottom: 2px solid var(--border-color); text-align:left;">
                        <th style="padding:12px;">Roll No</th>
                        <th style="padding:12px;">Student Email</th>
                        <th style="padding:12px; width: 180px;">Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        enrollments.forEach(e => {
            const status = attMap[e.student_user_id] || '';
            html += `
                <tr style="border-bottom: 1px solid var(--border-color);">
                    <td style="padding:12px;">${e.roll_no}</td>
                    <td style="padding:12px;">${e.email}</td>
                    <td style="padding:12px;">
                        <select class="form-control fc-attendance-status-select" data-user-id="${e.student_user_id}" style="width:100%; padding:6px 8px;">
                            <option value="PRESENT" ${status === 'PRESENT' ? 'selected' : ''}>PRESENT</option>
                            <option value="ABSENT" ${status === 'ABSENT' ? 'selected' : ''}>ABSENT</option>
                            <option value="LATE" ${status === 'LATE' ? 'selected' : ''}>LATE</option>
                            <option value="EXCUSED" ${status === 'EXCUSED' ? 'selected' : ''}>EXCUSED</option>
                        </select>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        roster.innerHTML = html;
    } catch (err) {
        roster.innerHTML = `<p style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

$('#fc-btn-show-create-session').addEventListener('click', () => {
    $('#fc-create-session-form-container').style.display = 'block';
});
$('#fc-btn-cancel-session').addEventListener('click', () => {
    $('#fc-create-session-form-container').style.display = 'none';
    $('#fc-form-create-session').reset();
});

$('#fc-form-create-session').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!state.currentOfferingId) return toast('Offering context lost', 'error');

    const btn = $('#fc-btn-submit-session');
    setLoading(btn, true);
    
    try {
        await apiFetch(`/offerings/${state.currentOfferingId}/sessions`, {
            method: 'POST',
            body: JSON.stringify({
                session_date: $('#fc-session-date').value,
                topic: $('#fc-session-topic').value || null
            })
        });
        toast('Session created!', 'success');
        $('#fc-form-create-session').reset();
        $('#fc-create-session-form-container').style.display = 'none';
        loadCourseAttendance(state.currentOfferingId);
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

$('#fc-btn-save-attendance').addEventListener('click', async () => {
    if (!fcCurrentSessionId) return;
    
    const records = [];
    $$('.fc-attendance-status-select').forEach(select => {
        records.push({
            student_user_id: parseInt(select.dataset.userId),
            status: select.value
        });
    });

    const btn = $('#fc-btn-save-attendance');
    setLoading(btn, true);
    
    try {
        await apiFetch(`/sessions/${fcCurrentSessionId}/attendance/bulk`, {
            method: 'POST',
            body: JSON.stringify({ records })
        });
        toast('Attendance saved!', 'success');
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

// ----------------------------------------
// FACULTY COURSE: ASSESSMENTS
// ----------------------------------------
let fcCurrentAssessmentId = null;

async function loadCourseAssessments(offeringId) {
    const list = $('#fc-assessments-list');
    const gradingContainer = $('#fc-assessment-grading-container');
    
    gradingContainer.style.display = 'none';
    list.innerHTML = '<p class="empty-state">Loading assessments...</p>';

    try {
        const assessments = await apiFetch(`/offerings/${offeringId}/assessments`);
        if (assessments.length === 0) {
            list.innerHTML = '<p class="empty-state">No assessments created yet.</p>';
            return;
        }

        list.innerHTML = '';
        assessments.forEach(a => {
            const btn = document.createElement('button');
            btn.className = 'btn';
            btn.style.cssText = 'background: white; border: 1px solid var(--border-color); color: var(--text-color); white-space: nowrap; padding: 6px 12px;';
            btn.textContent = `${a.title} (${a.type})`;
            btn.onclick = () => loadFcAssessmentGrading(offeringId, a);
            list.appendChild(btn);
        });
    } catch (err) {
        list.innerHTML = `<p style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

async function loadFcAssessmentGrading(offeringId, assessment) {
    fcCurrentAssessmentId = assessment.assessment_id;
    const gradingContainer = $('#fc-assessment-grading-container');
    const roster = $('#fc-assessment-roster');
    
    gradingContainer.style.display = 'block';
    $('#fc-current-assessment-label').textContent = `Assessment: ${assessment.title}`;
    $('#fc-current-assessment-meta').textContent = `Type: ${assessment.type} | Max Marks: ${assessment.max_marks} | Weight: ${assessment.weightage}%`;
    roster.innerHTML = '<p>Loading students...</p>';

    try {
        const [enrollments, scores] = await Promise.all([
            apiFetch(`/offerings/${offeringId}/enrollments`),
            apiFetch(`/assessments/${assessment.assessment_id}/scores`)
        ]);

        if (enrollments.length === 0) {
            roster.innerHTML = '<p class="empty-state">No students enrolled.</p>';
            return;
        }

        const scoreMap = {};
        scores.forEach(s => scoreMap[s.student_user_id] = s.marks);

        let html = '';
        enrollments.forEach(e => {
            const currentScore = scoreMap[e.student_user_id] !== undefined ? scoreMap[e.student_user_id] : '';
            html += `
                <div class="card" style="padding: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0;">${e.email}</h4>
                        <p style="margin: 4px 0 0 0; font-size: 13px; color: var(--text-secondary);">Roll No: ${e.roll_no}</p>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="number" class="form-control" id="score-input-${e.student_user_id}" 
                               value="${currentScore}" placeholder="Score" style="width: 80px;" min="0" max="${assessment.max_marks}">
                        <span style="color: var(--text-secondary);">/ ${assessment.max_marks}</span>
                        <button class="btn btn-primary btn-sm" onclick="saveStudentScore(${assessment.assessment_id}, ${e.student_user_id}, this)">Save</button>
                    </div>
                </div>
            `;
        });

        roster.innerHTML = html;
    } catch (err) {
        roster.innerHTML = `<p style="color:var(--color-error)">Error: ${err.message}</p>`;
    }
}

window.saveStudentScore = async function(assessmentId, studentUserId, btnEl) {
    const inputEl = document.getElementById(`score-input-${studentUserId}`);
    const marks = parseFloat(inputEl.value);
    
    if (isNaN(marks)) return toast('Please enter a valid score', 'error');

    const originalText = btnEl.textContent;
    btnEl.textContent = 'Saving...';
    btnEl.disabled = true;

    try {
        await apiFetch(`/assessments/${assessmentId}/scores`, {
            method: 'POST',
            body: JSON.stringify({
                student_user_id: studentUserId,
                marks: marks
            })
        });
        toast('Score saved', 'success');
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        btnEl.textContent = originalText;
        btnEl.disabled = false;
    }
};

$('#fc-btn-show-create-assessment').addEventListener('click', () => {
    $('#fc-create-assessment-form-container').style.display = 'block';
});
$('#fc-btn-cancel-assessment').addEventListener('click', () => {
    $('#fc-create-assessment-form-container').style.display = 'none';
    $('#fc-form-create-assessment').reset();
});

$('#fc-form-create-assessment').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!state.currentOfferingId) return toast('Offering context lost', 'error');

    const btn = $('#fc-btn-submit-assessment');
    setLoading(btn, true);
    
    try {
        await apiFetch(`/offerings/${state.currentOfferingId}/assessments`, {
            method: 'POST',
            body: JSON.stringify({
                title: $('#fc-assessment-title').value,
                type: $('#fc-assessment-type').value,
                max_marks: parseFloat($('#fc-assessment-max-marks').value),
                weightage: parseFloat($('#fc-assessment-weightage').value),
                assessment_date: $('#fc-assessment-date').value
            })
        });
        toast('Assessment created!', 'success');
        $('#fc-form-create-assessment').reset();
        $('#fc-create-assessment-form-container').style.display = 'none';
        loadCourseAssessments(state.currentOfferingId);
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        setLoading(btn, false);
    }
});

async function renderCourseRoster(offeringId) {
    const list = $('#faculty-roster-list');
    const countDisplay = $('#roster-count');
    list.innerHTML = '<p class="empty-state">Loading roster...</p>';
    countDisplay.textContent = 'Loading...';

    try {
        const enrollments = await apiFetch(`/offerings/${offeringId}/enrollments`);
        countDisplay.textContent = `${enrollments.length} Students`;
        
        if (enrollments.length === 0) {
            list.innerHTML = '<p class="empty-state">No students are currently enrolled in this class.</p>';
            return;
        }

        let html = '';
        enrollments.forEach(e => {
            html += `
                <div class="card" style="padding:0; overflow:hidden;">
                    <div style="padding: 16px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; background: #fff;" 
                         onclick="toggleStudentExpand(${e.student_user_id}, ${offeringId}, this)">
                        <div>
                            <h4 style="color:var(--primary); margin:0;">${e.email}</h4>
                            <p style="margin:4px 0 0 0; font-size:14px; color:var(--text-secondary);">Roll No: ${e.roll_no}</p>
                        </div>
                        <span style="font-size: 12px; color: var(--primary);">▼ Expand</span>
                    </div>
                    <div id="student-expand-${e.student_user_id}" style="display:none; padding: 16px; border-top: 1px solid var(--border-color); background: #f8fafc;">
                        <div style="display:flex; gap:16px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0;">
                            <button type="button" class="student-tab active" onclick="loadStudentCourseData(${e.student_user_id}, ${offeringId}, 'attendance', this)" style="background:none; border:none; padding:8px 16px; cursor:pointer; font-weight:500; border-bottom: 2px solid var(--primary); color:var(--primary);">Attendance</button>
                            <button type="button" class="student-tab" onclick="loadStudentCourseData(${e.student_user_id}, ${offeringId}, 'assessment', this)" style="background:none; border:none; padding:8px 16px; cursor:pointer; font-weight:500; color:var(--text-secondary);">Assessments</button>
                        </div>
                        <div id="student-data-container-${e.student_user_id}">
                            Loading...
                        </div>
                    </div>
                </div>
            `;
        });
        list.innerHTML = html;
    } catch (err) {
        list.innerHTML = `<p class="empty-state" style="color:var(--color-error)">Error: ${err.message}</p>`;
        countDisplay.textContent = 'Error';
    }
}

function toggleStudentExpand(userId, offeringId, headerEl) {
    try {
        const expandDiv = document.getElementById(`student-expand-${userId}`);
        if (!expandDiv) return;
        
        const isHidden = expandDiv.style.display === 'none';
        expandDiv.style.display = isHidden ? 'block' : 'none';
        
        const span = headerEl.querySelector('span');
        if (span) span.textContent = isHidden ? '▲ Collapse' : '▼ Expand';
        
        if (isHidden && !expandDiv.dataset.loaded) {
            expandDiv.dataset.loaded = 'true';
            const defaultTab = expandDiv.querySelector('.student-tab');
            if (typeof loadStudentCourseData === 'function') {
                loadStudentCourseData(userId, offeringId, 'attendance', defaultTab);
            } else if (window.loadStudentCourseData) {
                window.loadStudentCourseData(userId, offeringId, 'attendance', defaultTab);
            } else {
                expandDiv.querySelector(`div[id="student-data-container-${userId}"]`).innerHTML = 'Error: loadStudentCourseData is not defined.';
            }
        }
    } catch (err) {
        alert('Error expanding student: ' + err.message);
    }
}

async function loadStudentCourseData(userId, offeringId, type, tabBtn) {
    const container = document.getElementById(`student-data-container-${userId}`);
    if (!container) return;

    try {
        // Safely update tabs UI
        if (tabBtn && tabBtn.parentElement) {
            const tabContainer = tabBtn.parentElement;
            tabContainer.querySelectorAll('.student-tab').forEach(b => {
                b.style.borderBottom = 'none';
                b.style.color = 'var(--text-secondary)';
            });
            tabBtn.style.borderBottom = '2px solid var(--primary)';
            tabBtn.style.color = 'var(--primary)';
        }

        container.innerHTML = '<p style="font-size:14px; color:var(--text-secondary);">Fetching data...</p>';

        if (type === 'attendance') {
            const att = await apiFetch(`/students/${userId}/attendance/${offeringId}`);
            container.innerHTML = `
                <div style="display:flex; gap:24px; padding: 12px; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
                    <div><span style="font-size:12px; color:var(--text-secondary); display:block;">Total</span><span style="font-weight:600;">${att.total_sessions}</span></div>
                    <div><span style="font-size:12px; color:var(--text-secondary); display:block;">Present</span><span style="color:green; font-weight:600;">${att.present}</span></div>
                    <div><span style="font-size:12px; color:var(--text-secondary); display:block;">Absent</span><span style="color:red; font-weight:600;">${att.absent}</span></div>
                    <div><span style="font-size:12px; color:var(--text-secondary); display:block;">Late</span><span style="color:orange; font-weight:600;">${att.late}</span></div>
                    <div><span style="font-size:12px; color:var(--text-secondary); display:block;">%</span><span style="font-weight:600;">${att.attendance_percentage.toFixed(1)}%</span></div>
                </div>
            `;
        } else if (type === 'assessment') {
            const perf = await apiFetch(`/students/${userId}/performance/${offeringId}`);
            if (!perf.scores || perf.scores.length === 0) {
                container.innerHTML = '<p style="font-size:14px; color:var(--text-secondary);">No assessments recorded for this student.</p>';
                return;
            }
            let html = '<table class="table" style="background:white;"><thead><tr><th>Assessment</th><th>Type</th><th>Score / Max</th><th>Weight</th></tr></thead><tbody>';
            perf.scores.forEach(s => {
                html += `
                    <tr>
                        <td>${s.assessment_title}</td>
                        <td>${s.type}</td>
                        <td><strong>${s.score_marks}</strong> / ${s.max_marks}</td>
                        <td>${s.weightage}%</td>
                    </tr>
                `;
            });
            html += '</tbody></table>';
            html += `<p style="font-size:14px; margin-top:8px;"><strong>Total Weighted Score:</strong> ${perf.total_weighted_score.toFixed(2)} out of ${perf.weightage_covered}% evaluated</p>`;
            container.innerHTML = html;
        }
    } catch (err) {
        container.innerHTML = `<p style="font-size:14px; color:var(--color-error);">Error fetching ${type}: ${err.message}</p>`;
    }
}
// Attach to window just in case inline handlers need it explicitly
window.loadStudentCourseData = loadStudentCourseData;
window.toggleStudentExpand = toggleStudentExpand;

// ============================================
// INIT
// ============================================

(function init() {
    if (state.token && state.userId) {
        loadDashboard();
    } else {
        showView('auth');
    }
})();
