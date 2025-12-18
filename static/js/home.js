let slideIndex = 0;
const slides = document.querySelectorAll('.slide');

function showSlides() {
    slides.forEach((slide, index) => {
    slide.style.opacity = (index === slideIndex) ? '1' : '0';
});
slideIndex = (slideIndex + 1) % slides.length;
}

setInterval(showSlides, 3000); // Change image every 3 seconds
showSlides(); // Initial call
