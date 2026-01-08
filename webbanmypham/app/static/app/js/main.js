// // ================================
//         // STICKY MENU ON SCROLL
//         // ================================
//         const header = document.querySelector('.header');
//         const navbarMenu = document.querySelector('.navbar__menu');
//         const menuPlaceholder = document.querySelector('.menu-placeholder');
        
//         // Lấy vị trí ban đầu của menu
//         const menuOffsetTop = navbarMenu.offsetTop;
        
//         // Ngưỡng scroll để kích hoạt sticky (có thể điều chỉnh)
//         const scrollThreshold = 150; // 150px
        
//         let isSticky = false;
        
//         window.addEventListener('scroll', () => {
//             const scrollPosition = window.scrollY;
            
//             // Khi scroll vượt qua ngưỡng
//             if (scrollPosition > scrollThreshold && !isSticky) {
//                 // Kích hoạt sticky menu
//                 navbarMenu.classList.add('sticky');
//                 menuPlaceholder.classList.add('active');
//                 isSticky = true;
                
//                 // Log để debug (có thể xóa sau)
//                 console.log('Menu is now sticky');
//             } 
//             // Khi scroll lên trên ngưỡng
//             else if (scrollPosition <= scrollThreshold && isSticky) {
//                 // Hủy sticky menu
//                 navbarMenu.classList.remove('sticky');
//                 menuPlaceholder.classList.remove('active');
//                 isSticky = false;
                
//                 console.log('Menu is back to normal');
//             }
//         });

//         // ================================
//         // SEARCH FORM ANIMATION
//         // ================================
//         const searchInput = document.querySelector('.search-input');
//         const searchBtn = document.querySelector('.search-btn');
        
//         searchInput.addEventListener('focus', () => {
//             searchBtn.style.transform = 'scale(1.05)';
//         });
        
//         searchInput.addEventListener('blur', () => {
//             searchBtn.style.transform = 'scale(1)';
//         });

//         // ================================
//         // UPDATE BADGE FUNCTION
//         // ================================
//         function updateBadge(selector, count) {
//             const badge = document.querySelector(selector);
//             if (badge) {
//                 badge.textContent = count;
//                 badge.style.animation = 'pulse 0.5s ease-in-out';
//                 setTimeout(() => {
//                     badge.style.animation = '';
//                 }, 500);
//             }
//         }

//         // ================================
//         // DEMO: UPDATE BADGES ON CLICK
//         // ================================
//         document.querySelector('.wishlist-btn').addEventListener('click', (e) => {
//             e.preventDefault();
//             const currentCount = parseInt(document.querySelector('.wishlist-btn .badge').textContent);
//             updateBadge('.wishlist-btn .badge', currentCount + 1);
//         });

//         document.querySelector('.cart-btn').addEventListener('click', (e) => {
//             e.preventDefault();
//             const currentCount = parseInt(document.querySelector('.cart-btn .badge').textContent);
//             updateBadge('.cart-btn .badge', currentCount + 1);
//         });

//         // ================================
//         // SMOOTH SCROLL FOR NAVIGATION
//         // ================================
//         document.querySelectorAll('.main-nav-links a').forEach(link => {
//             link.addEventListener('click', (e) => {
//                 // Chỉ áp dụng smooth scroll nếu link có href bắt đầu bằng #
//                 if (link.getAttribute('href').startsWith('#')) {
//                     e.preventDefault();
//                     const targetId = link.getAttribute('href');
//                     const targetElement = document.querySelector(targetId);
                    
//                     if (targetElement) {
//                         const offsetTop = targetElement.offsetTop - 100; // Trừ đi chiều cao menu
//                         window.scrollTo({
//                             top: offsetTop,
//                             behavior: 'smooth'
//                         });
//                     }
//                 }
//             });
//         });

//         // ================================
//         // SCROLL TO TOP WHEN CLICK LOGO
//         // ================================
//         document.querySelector('.navbar__menu-logo a').addEventListener('click', (e) => {
//             if (window.scrollY > 0) {
//                 e.preventDefault();
//                 window.scrollTo({
//                     top: 0,
//                     behavior: 'smooth'
//                 });
//             }
//         });

//         // ================================
//         // SHOW/HIDE SCROLL PROGRESS (Optional)
//         // ================================
//         function updateScrollProgress() {
//             const windowHeight = window.innerHeight;
//             const documentHeight = document.documentElement.scrollHeight;
//             const scrollTop = window.scrollY;
//             const scrollPercent = (scrollTop / (documentHeight - windowHeight)) * 100;
            
//             // Có thể sử dụng để tạo progress bar
//             // document.querySelector('.scroll-progress').style.width = scrollPercent + '%';
//         }

//         window.addEventListener('scroll', updateScrollProgress);

//         // ================================
//         // INITIALIZATION
//         // ================================
//         console.log('Header JavaScript initialized');
//         console.log('Scroll threshold:', scrollThreshold + 'px');
// =================================================================================================================================
// slider chính
let currentSlide = 0;
const totalSlides = 5;
const slideWrapper = document.querySelector(".slide-wrapper");
const dots = document.querySelectorAll(".indicator-dot");

// Hàm cập nhật vị trí slide
function updateSlide() {
  slideWrapper.style.transform = `translateX(-${currentSlide * 100}%)`;

  // Cập nhật dots
  dots.forEach((dot, index) => {
    dot.classList.toggle("active", index === currentSlide);
  });
}

// Chuyển sang slide tiếp theo
function nextSlide() {
  currentSlide = (currentSlide + 1) % totalSlides;
  updateSlide();
}

// Chuyển về slide trước
function prevSlide() {
  currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
  updateSlide();
}

// Đi đến slide cụ thể
function goToSlide(index) {
  currentSlide = index;
  updateSlide();
}

// Tự động chuyển slide sau 5 giây
let autoSlide = setInterval(nextSlide, 5000);

// Dừng auto-slide khi hover vào slider
const slideContainer = document.querySelector(".slide-container");
slideContainer.addEventListener("mouseenter", () => {
  clearInterval(autoSlide);
});

// Tiếp tục auto-slide khi rời khỏi slider
slideContainer.addEventListener("mouseleave", () => {
  autoSlide = setInterval(nextSlide, 5000);
});

// Hỗ trợ phím mũi tên
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft") {
    prevSlide();
  } else if (e.key === "ArrowRight") {
    nextSlide();
  }
});

// Hỗ trợ touch swipe trên mobile
let touchStartX = 0;
let touchEndX = 0;

slideContainer.addEventListener("touchstart", (e) => {
  touchStartX = e.changedTouches[0].screenX;
});

slideContainer.addEventListener("touchend", (e) => {
  touchEndX = e.changedTouches[0].screenX;
  handleSwipe();
});

function handleSwipe() {
  if (touchStartX - touchEndX > 50) {
    nextSlide();
  }
  if (touchEndX - touchStartX > 50) {
    prevSlide();
  }
}



// -----------------------------------
// js cho offers carousel
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.carousel-container');
    const prevBtn = document.querySelector('.arrow.prev');
    const nextBtn = document.querySelector('.arrow.next');
    let currentPosition = 0;
    let products = [];

    // Khởi tạo carousel
    function initCarousel() {
        // Lấy tất cả product cards
        products = Array.from(container.querySelectorAll('.product-card'));
        
        // Ẩn các sản phẩm ngoài viewport ban đầu (từ index 4 trở đi)
        products.forEach((product, index) => {
            if (index >= 4) {
                product.style.display = 'none';
            }
        });

        // Disable nút prev ban đầu
        updateNavigationButtons();
    }

    // Cập nhật trạng thái các nút điều hướng
    function updateNavigationButtons() {
        prevBtn.disabled = currentPosition === 0;
        nextBtn.disabled = currentPosition >= products.length - 4;
    }

    // Xử lý khi click nút next
    function handleNext() {
        if (currentPosition < products.length - 4) {
            // Ẩn sản phẩm đầu tiên của view hiện tại
            products[currentPosition].style.display = 'none';
            
            // Hiện sản phẩm tiếp theo
            products[currentPosition + 4].style.display = '';
            
            currentPosition++;
            updateNavigationButtons();
        }
    }

    // Xử lý khi click nút previous
    function handlePrev() {
        if (currentPosition > 0) {
            // Hiện lại sản phẩm trước đó
            products[currentPosition - 1].style.display = '';
            
            // Ẩn sản phẩm cuối của view hiện tại
            products[currentPosition + 3].style.display = 'none';
            
            currentPosition--;
            updateNavigationButtons();
        }
    }

    // Thêm event listeners
    nextBtn.addEventListener('click', handleNext);
    prevBtn.addEventListener('click', handlePrev);

    // Khởi tạo carousel khi trang load xong
    initCarousel();
});

// ----------------------------------------------


 



