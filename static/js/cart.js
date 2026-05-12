// Инициализация корзины
function getCart() {
    const cart = localStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateHeaderCart();
}

// Обновление счетчиков в шапке
function updateHeaderCart() {
    const cart = getCart();
    const count = cart.reduce((sum, item) => sum + parseInt(item.quantity), 0);
    const total = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    
    const countEl = document.getElementById('cart-count');
    const totalEl = document.getElementById('cart-total-price');
    
    if (countEl) countEl.innerText = count;
    if (totalEl) totalEl.innerText = total.toFixed(2);
}

// Добавление в корзину
function addToCart(id, name, price, quantity = 1, btnEl = null) {
    let cart = getCart();
    const existing = cart.find(item => item.id === id);
    
    if (existing) {
        existing.quantity += parseInt(quantity);
    } else {
        cart.push({ id, name, price: parseFloat(price), quantity: parseInt(quantity) });
    }
    
    saveCart(cart);
    
    // Визуальное подтверждение
    if (btnEl) {
        if (window.AppAnimations) {
            window.AppAnimations.iconTransition(btnEl, 1);
            window.AppAnimations.createBurst(btnEl);
            
            // Возврат через 2 секунды
            setTimeout(() => {
                window.AppAnimations.iconTransition(btnEl, 0);
            }, 2000);
        } else {
            const iconPlus = btnEl.querySelector('.icon-plus, .icon-cart');
            const iconCheck = btnEl.querySelector('.icon-check');
            if (iconPlus) iconPlus.classList.add('hidden');
            if (iconCheck) iconCheck.classList.remove('hidden');
            
            setTimeout(() => {
                if (iconPlus) iconPlus.classList.remove('hidden');
                if (iconCheck) iconCheck.classList.add('hidden');
            }, 2000);
        }
    }
}

// Удаление из корзины
function removeFromCart(id) {
    let cart = getCart();
    cart = cart.filter(item => item.id !== id);
    saveCart(cart);
    renderCart(); // Перерисовка страницы корзины
}

// Изменение количества
function changeQuantity(id, newQty) {
    if (newQty < 1) return;
    let cart = getCart();
    const item = cart.find(item => item.id === id);
    if (item) {
        item.quantity = parseInt(newQty);
        saveCart(cart);
        renderCart();
    }
}

// Отрисовка страницы корзины
function renderCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    if (!cartItemsContainer) return;

    const cart = getCart();
    cartItemsContainer.innerHTML = '';
    
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p>Ваша корзина пуста.</p>';
        document.getElementById('checkout-btn').style.display = 'none';
        document.getElementById('checkout-form-container').style.display = 'none';
        document.getElementById('cart-total-sum').innerText = '0.00';
        return;
    }

    let total = 0;
    
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        const html = `
            <div class="rounded-[1.5rem] border border-border/70 bg-white p-5 shadow-sm flex flex-col sm:flex-row sm:items-center gap-4">
                <div class="flex-grow">
                    <h4 class="font-display text-xl font-bold text-steel-950">${item.name}</h4>
                    <div class="text-sm font-semibold text-emerald-600 mt-1">${parseFloat(item.price).toFixed(2)} ₸ / шт</div>
                </div>
                <div class="flex items-center justify-between sm:justify-end gap-4 w-full sm:w-auto">
                    <input type="number" class="rounded-xl border border-border p-2 w-20 text-center focus:ring-2 focus:ring-ember-500 outline-none" value="${item.quantity}" min="1" onchange="changeQuantity('${item.id}', this.value)">
                    <div class="font-bold text-lg text-steel-950 min-w-24 text-right">
                        ${itemTotal.toFixed(2)} ₸
                    </div>
                    <button class="flex items-center justify-center w-10 h-10 rounded-xl bg-red-50 text-red-600 transition hover:bg-red-100" onclick="removeFromCart('${item.id}')" title="Удалить">
                       <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trash-2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                    </button>
                </div>
            </div>
        `;
        cartItemsContainer.insertAdjacentHTML('beforeend', html);
    });
    
    document.getElementById('cart-total-sum').innerText = total.toFixed(2);
    document.getElementById('checkout-btn').style.display = 'inline-flex';
    
    // Перерисовать иконки для новых элементов
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Слушатели событий
document.addEventListener('DOMContentLoaded', () => {
    
    // Кнопка добавления в списке товаров
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const name = this.getAttribute('data-name');
            const price = this.getAttribute('data-price');
            addToCart(id, name, price, 1, this);
        });
    });

    // Кнопка добавления на карточке товара
    document.querySelectorAll('.add-to-cart-detail').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const name = this.getAttribute('data-name');
            const price = this.getAttribute('data-price');
            const qtyInput = document.getElementById(`qty-input-${id}`);
            const qty = qtyInput ? qtyInput.value : 1;
            addToCart(id, name, price, qty, this);
        });
    });

    // Отрисовка корзины если мы на её странице
    if (document.getElementById('cart-items')) {
        renderCart();
    }

    // Показать форму оформления заказа
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            document.getElementById('checkout-form-container').style.display = 'block';
            checkoutBtn.style.display = 'none';
        });
    }

    // Обработка оформления заказа(Submit form)
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const cart = getCart();
            
            const userInfo = {
                first_name: document.getElementById('first_name').value,
                last_name: document.getElementById('last_name').value,
                email: document.getElementById('email').value,
                address: document.getElementById('address').value,
                postal_code: document.getElementById('postal_code').value,
                city: document.getElementById('city').value,
            };

            const payload = {
                user_info: userInfo,
                cart: cart.map(item => ({
                    product_id: item.id,
                    price: item.price,
                    quantity: item.quantity
                }))
            };

            fetch('/order/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert('Ошибка: ' + data.error);
                } else {
                    document.getElementById('order-message').innerHTML = `<p style="color: green;">${data.message}</p>`;
                    localStorage.removeItem('cart');
                    updateHeaderCart();
                    document.getElementById('cart-items').innerHTML = '';
                    document.getElementById('checkout-form').reset();
                    document.getElementById('checkout-form').style.display = 'none';
                    document.getElementById('cart-total-sum').innerText = '0.00';
                }
            })
            .catch(err => {
                console.error(err);
                alert('Произошла ошибка при оформлении заказа');
            });
        });
    }
});
