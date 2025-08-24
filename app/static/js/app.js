// AI Language Tutor App - Basic JavaScript
// Personal Family Educational Tool

console.log('🎯 AI Language Tutor App - Frontend Loaded');
console.log('📱 Personal Family Educational Tool');
console.log('⚡ FastHTML + MonsterUI Ready');

// Basic app initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM Content Loaded');
    
    // Add some basic interactivity
    const title = document.querySelector('.title');
    if (title) {
        title.addEventListener('click', function() {
            console.log('🎯 AI Language Tutor App clicked!');
        });
    }
    
    // Check if we're running as PWA
    if (window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches) {
        console.log('📱 Running as PWA');
    }
});