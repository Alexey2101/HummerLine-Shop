lucide.createIcons();
document.addEventListener('DOMContentLoaded', () => {
    if (typeof updateHeaderCart === 'function') {
        updateHeaderCart();
    }

    const profileBtn = document.getElementById('profile-dropdown-btn');
    const profileMenu = document.getElementById('profile-dropdown-menu');
    const profileIcon = document.getElementById('profile-dropdown-icon');

    if (profileBtn && profileMenu) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            profileMenu.classList.toggle('opacity-0');
            profileMenu.classList.toggle('invisible');
            profileMenu.classList.toggle('translate-y-2');
            if (profileIcon) {
                profileIcon.classList.toggle('rotate-180');
            }
        });

        document.addEventListener('click', (e) => {
            if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
                profileMenu.classList.add('opacity-0', 'invisible', 'translate-y-2');
                if (profileIcon) {
                    profileIcon.classList.remove('rotate-180');
                }
            }
        });
    }

    // Ограничение ввода только цифр для полей с ценами и фильтрами
    const numericInputs = document.querySelectorAll('input[type="number"], .numeric-only');
    numericInputs.forEach(input => {
        input.addEventListener('keydown', (e) => {
            // Разрешаем: backspace, delete, tab, escape, enter
            if ([46, 8, 9, 27, 13].indexOf(e.keyCode) !== -1 ||
                // Разрешаем: Ctrl+A, Command+A, Ctrl+C, Ctrl+V, Ctrl+X
                ((e.keyCode === 65 || e.keyCode === 67 || e.keyCode === 86 || e.keyCode === 88) && (e.ctrlKey === true || e.metaKey === true)) ||
                // Разрешаем: home, end, left, right
                (e.keyCode >= 35 && e.keyCode <= 40)) {
                return;
            }
            // Разрешаем точку или запятую (только одну) для десятичных цен
            if ((e.key === '.' || e.key === ',') && !input.value.includes('.') && !input.value.includes(',')) {
                return;
            }
            // Блокируем всё остальное, если это не цифра
            if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
                e.preventDefault();
            }
        });

        // Дополнительная проверка при вставке (paste)
        input.addEventListener('paste', (e) => {
            const pasteData = e.clipboardData.getData('text');
            if (!/^\d*[.,]?\d*$/.test(pasteData)) {
                e.preventDefault();
            }
        });
    });

    // GSAP Animations moved to animations.js
});
document.querySelectorAll('.favorite-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const btnEl = e.currentTarget;
        const productId = btnEl.dataset.id;
        
        try {
            const response = await fetch(`/favorites/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                const icon = btnEl.querySelector('svg');
                if (data.is_favorite) {
                    icon.classList.add('is-favorite');
                    if (window.AppAnimations) {
                        window.AppAnimations.favoriteAdd(btnEl, e);
                    }
                } else {
                    icon.classList.remove('is-favorite');
                    if (window.AppAnimations) {
                        window.AppAnimations.favoriteRemove(icon);
                    }
                    // Если мы находимся на странице избранного, скроем карточку
                    if (window.location.pathname.includes('/favorites/')) {
                        const card = document.getElementById(`product-card-${productId}`);
                        if (card) {
                            if (window.AppAnimations) {
                                window.AppAnimations.favoriteCardRemove(card);
                            } else {
                                card.remove();
                            }
                        }
                    }
                }
            }
        } catch(err) {
            console.error(err);
        }
    });
});
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}