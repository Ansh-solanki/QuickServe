document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const proFields = document.getElementById('proFields');
  
    if (signupForm) {
      const userTypeRadios = signupForm.querySelectorAll('input[name="userType"]');
      userTypeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
          if (e.target.value === 'quickpro') {
            proFields.classList.remove('hidden');
          } else {
            proFields.classList.add('hidden');
          }
        });
      });
  
      signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(signupForm);
        const data = Object.fromEntries(formData);
        console.log('Signup data:', data);
        // TODO: Add API integration
        alert('Signup functionality will be implemented with backend integration');
      });
    }
  
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const data = Object.fromEntries(formData);
        console.log('Login data:', data);
        // TODO: Add API integration
        alert('Login functionality will be implemented with backend integration');
      });
    }
  });