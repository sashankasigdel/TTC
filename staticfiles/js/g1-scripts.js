    // Simple script for load more functionality
    document.addEventListener('DOMContentLoaded', function() {
      const loadMoreBtn = document.querySelector('.btn-outline');
      
      loadMoreBtn.addEventListener('click', function(e) {
        e.preventDefault();
        alert('More chapters will be loaded here. Currently showing first 10 chapters.');
      });
    });