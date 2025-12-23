// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');
  
  menuToggle.addEventListener('click', function() {
    navLinks.classList.toggle('active');
  });
  
  // Close menu when clicking on a link
  const navItems = document.querySelectorAll('#nav-links a');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navLinks.classList.remove('active');
    });
  });
  
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80,
          behavior: 'smooth'
        });
      }
    });
  });
});

// Dropdown functionality for mobile
document.addEventListener('DOMContentLoaded', function() {
  const loginBtn = document.getElementById('loginBtn');
  const loginDropdown = document.querySelector('.login-dropdown-menu');
  const userBtn = document.getElementById('userBtn');
  const userDropdown = document.querySelector('.user-dropdown-menu');
  
  // Toggle login dropdown on mobile
  if (loginBtn && loginDropdown) {
    loginBtn.addEventListener('click', function(e) {
      if (window.innerWidth <= 768) {
        e.preventDefault();
        loginDropdown.style.display = 
          loginDropdown.style.display === 'block' ? 'none' : 'block';
      }
    });
  }
  
  // Toggle user dropdown on mobile
  if (userBtn && userDropdown) {
    userBtn.addEventListener('click', function(e) {
      if (window.innerWidth <= 768) {
        e.preventDefault();
        userDropdown.style.display = 
          userDropdown.style.display === 'block' ? 'none' : 'block';
      }
    });
  }
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.login-dropdown') && loginDropdown) {
      loginDropdown.style.display = 'none';
    }
    if (!e.target.closest('.user-dropdown') && userDropdown) {
      userDropdown.style.display = 'none';
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
    const loginBtn = document.getElementById('loginBtn');
    const loginDropdown = document.getElementById('loginDropdown');

    loginBtn.addEventListener('click', function(e) {
        e.preventDefault();
        loginDropdown.style.display = loginDropdown.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', function(e) {
        if (!loginBtn.contains(e.target) && !loginDropdown.contains(e.target)) {
            loginDropdown.style.display = 'none';
        }
    });
});

