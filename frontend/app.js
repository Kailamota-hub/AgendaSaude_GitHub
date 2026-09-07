const state = {
  token: localStorage.getItem('agendasaude_token') || '',
  user: null,
  doctors: [],
  selectedTime: '',
  rescheduleId: null,
};

const $ = (selector) => document.querySelector(selector);
const authSection = $('#authSection');
const appSection = $('#appSection');
const logoutButton = $('#logoutButton');
const toast = $('#toast');

function showToast(message, type = 'success') {
  toast.textContent = message;
  toast.className = `toast show ${type === 'error' ? 'error' : ''}`;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => { toast.className = 'toast'; }, 3000);
}

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  let data = {};
  try { data = await response.json(); } catch (_) { /* sem corpo JSON */ }
  if (!response.ok) throw new Error(data.error || `Erro HTTP ${response.status}`);
  return data;
}

function setAuthMode(mode) {
  const login = mode === 'login';
  $('#loginTab').classList.toggle('active', login);
  $('#registerTab').classList.toggle('active', !login);
  $('#loginForm').classList.toggle('hidden', !login);
  $('#registerForm').classList.toggle('hidden', login);
}

$('#loginTab').addEventListener('click', () => setAuthMode('login'));
$('#registerTab').addEventListener('click', () => setAuthMode('register'));

$('#loginForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const data = await api('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email: $('#loginEmail').value, password: $('#loginPassword').value }),
    });
    persistSession(data);
    await enterApp();
    showToast('Login realizado com sucesso.');
  } catch (error) { showToast(error.message, 'error'); }
});

$('#registerForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const data = await api('/api/register', {
      method: 'POST',
      body: JSON.stringify({
        name: $('#registerName').value,
        email: $('#registerEmail').value,
        password: $('#registerPassword').value,
      }),
    });
    persistSession(data);
    await enterApp();
    showToast('Cadastro criado com sucesso.');
  } catch (error) { showToast(error.message, 'error'); }
});

function persistSession(data) {
  state.token = data.token;
  state.user = data.user;
  localStorage.setItem('agendasaude_token', state.token);
}

logoutButton.addEventListener('click', async () => {
  try { await api('/api/logout', { method: 'POST', body: '{}' }); } catch (_) {}
  state.token = '';
  state.user = null;
  state.rescheduleId = null;
  localStorage.removeItem('agendasaude_token');
  appSection.classList.add('hidden');
  logoutButton.classList.add('hidden');
  authSection.classList.remove('hidden');
});

async function enterApp() {
  authSection.classList.add('hidden');
  appSection.classList.remove('hidden');
  logoutButton.classList.remove('hidden');
  if (!state.user) {
    const me = await api('/api/me');
    state.user = me.user;
  }
  $('#welcomeTitle').textContent = `Olá, ${state.user.name.split(' ')[0]}!`;
  setMinimumDate();
  await loadDoctors();
  await loadAppointments();
}

function setMinimumDate() {
  const today = new Date();
  const offset = today.getTimezoneOffset();
  const local = new Date(today.getTime() - offset * 60 * 1000).toISOString().slice(0, 10);
  $('#dateInput').min = local;
  if (!$('#dateInput').value) $('#dateInput').value = local;
}

async function loadDoctors() {
  const data = await api('/api/doctors');
  state.doctors = data.doctors;
  const select = $('#doctorSelect');
  select.innerHTML = '<option value="">Selecione uma opção</option>' + data.doctors
    .map((doctor) => `<option value="${doctor.id}">${escapeHtml(doctor.specialty)} — ${escapeHtml(doctor.name)}</option>`)
    .join('');
}

$('#doctorSelect').addEventListener('change', loadSlots);
$('#dateInput').addEventListener('change', loadSlots);

async function loadSlots() {
  const doctorId = $('#doctorSelect').value;
  const date = $('#dateInput').value;
  state.selectedTime = '';
  const container = $('#slotsContainer');
  if (!doctorId || !date) {
    container.className = 'slots empty-state';
    container.textContent = 'Selecione profissional e data.';
    return;
  }
  try {
    const data = await api(`/api/slots?doctor_id=${encodeURIComponent(doctorId)}&date=${encodeURIComponent(date)}`);
    if (!data.slots.length) {
      container.className = 'slots empty-state';
      container.textContent = 'Nenhum horário disponível nessa data.';
      return;
    }
    container.className = 'slots';
    container.innerHTML = data.slots.map((time) => `<button type="button" class="slot-button" data-time="${time}">${time}</button>`).join('');
    container.querySelectorAll('.slot-button').forEach((button) => {
      button.addEventListener('click', () => {
        state.selectedTime = button.dataset.time;
        container.querySelectorAll('.slot-button').forEach((b) => b.classList.remove('selected'));
        button.classList.add('selected');
      });
    });
  } catch (error) { showToast(error.message, 'error'); }
}

$('#appointmentForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!state.selectedTime) {
    showToast('Escolha um horário disponível.', 'error');
    return;
  }
  const payload = {
    doctor_id: Number($('#doctorSelect').value),
    date: $('#dateInput').value,
    time: state.selectedTime,
  };
  try {
    if (state.rescheduleId) {
      await api(`/api/appointments/${state.rescheduleId}`, { method: 'PUT', body: JSON.stringify(payload) });
      showToast('Consulta reagendada com sucesso.');
      resetRescheduleMode();
    } else {
      await api('/api/appointments', { method: 'POST', body: JSON.stringify(payload) });
      showToast('Consulta agendada com sucesso.');
    }
    state.selectedTime = '';
    await loadSlots();
    await loadAppointments();
  } catch (error) { showToast(error.message, 'error'); }
});

$('#refreshButton').addEventListener('click', loadAppointments);
$('#cancelRescheduleButton').addEventListener('click', resetRescheduleMode);

async function loadAppointments() {
  const data = await api('/api/appointments');
  const list = $('#appointmentsList');
  const active = data.appointments.filter((item) => item.status === 'AGENDADA');
  const cancelled = data.appointments.filter((item) => item.status === 'CANCELADA');
  $('#activeCount').textContent = active.length;
  $('#cancelledCount').textContent = cancelled.length;

  if (!data.appointments.length) {
    list.innerHTML = '<div class="empty-state">Você ainda não possui consultas cadastradas.</div>';
    return;
  }
  list.innerHTML = data.appointments.map(renderAppointment).join('');
  list.querySelectorAll('[data-action="cancel"]').forEach((button) => button.addEventListener('click', cancelAppointment));
  list.querySelectorAll('[data-action="reschedule"]').forEach((button) => button.addEventListener('click', beginReschedule));
}

function renderAppointment(item) {
  const dateObj = new Date(`${item.appointment_date}T12:00:00`);
  const day = String(dateObj.getDate()).padStart(2, '0');
  const month = dateObj.toLocaleDateString('pt-BR', { month: 'short' }).replace('.', '');
  const cancelled = item.status === 'CANCELADA';
  return `
    <article class="appointment-card ${cancelled ? 'cancelled' : ''}">
      <div class="appointment-main">
        <div class="date-badge"><strong>${day}</strong><span>${escapeHtml(month)}</span></div>
        <div class="appointment-info">
          <strong>${escapeHtml(item.specialty)} — ${escapeHtml(item.doctor_name)}</strong>
          <span>${formatDate(item.appointment_date)} às ${escapeHtml(item.appointment_time)}</span>
          <div><span class="status-tag">${escapeHtml(item.status)}</span></div>
        </div>
      </div>
      ${cancelled ? '' : `
        <div class="appointment-actions">
          <button class="small-button" data-action="reschedule" data-id="${item.id}" data-doctor="${item.doctor_id}" data-date="${item.appointment_date}">Reagendar</button>
          <button class="small-button danger" data-action="cancel" data-id="${item.id}">Cancelar</button>
        </div>`}
    </article>`;
}

async function cancelAppointment(event) {
  const id = event.currentTarget.dataset.id;
  if (!window.confirm('Deseja realmente cancelar esta consulta?')) return;
  try {
    await api(`/api/appointments/${id}`, { method: 'DELETE' });
    showToast('Consulta cancelada.');
    await loadAppointments();
    await loadSlots();
  } catch (error) { showToast(error.message, 'error'); }
}

async function beginReschedule(event) {
  const button = event.currentTarget;
  state.rescheduleId = Number(button.dataset.id);
  $('#doctorSelect').value = button.dataset.doctor;
  $('#dateInput').value = button.dataset.date;
  $('#bookingTitle').textContent = 'Reagendar consulta';
  $('#appointmentSubmit').textContent = 'Confirmar reagendamento';
  $('#cancelRescheduleButton').classList.remove('hidden');
  await loadSlots();
  document.querySelector('.booking-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetRescheduleMode() {
  state.rescheduleId = null;
  state.selectedTime = '';
  $('#bookingTitle').textContent = 'Agendar nova consulta';
  $('#appointmentSubmit').textContent = 'Confirmar agendamento';
  $('#cancelRescheduleButton').classList.add('hidden');
  $('#doctorSelect').value = '';
  setMinimumDate();
  $('#slotsContainer').className = 'slots empty-state';
  $('#slotsContainer').textContent = 'Selecione profissional e data.';
}

function formatDate(value) {
  return new Date(`${value}T12:00:00`).toLocaleDateString('pt-BR');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

(async function boot() {
  if (!state.token) return;
  try {
    await enterApp();
  } catch (_) {
    state.token = '';
    localStorage.removeItem('agendasaude_token');
    authSection.classList.remove('hidden');
    appSection.classList.add('hidden');
    logoutButton.classList.add('hidden');
  }
})();
