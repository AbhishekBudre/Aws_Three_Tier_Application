const API_URL = "/api/items";

const form = document.getElementById("inventory-form");
const itemIdInput = document.getElementById("item-id");
const productNameInput = document.getElementById("product-name");
const categoryInput = document.getElementById("category");
const quantityInput = document.getElementById("quantity");
const priceInput = document.getElementById("price");

const inventoryBody = document.getElementById("inventory-body");
const message = document.getElementById("message");

const submitButton = document.getElementById("submit-button");
const cancelButton = document.getElementById("cancel-button");

let inventory = [];

function showMessage(text, type = "success") {
    message.textContent = text;
    message.className = type;

    if (text) {
        setTimeout(() => {
            message.textContent = "";
            message.className = "";
        }, 4000);
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(value);
}

async function request(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Request failed");
    }

    return data;
}

async function loadInventory() {
    inventoryBody.innerHTML =
        '<tr><td colspan="7">Loading inventory...</td></tr>';

    try {
        inventory = await request(API_URL);
        renderInventory();
    } catch (error) {
        inventoryBody.innerHTML =
            '<tr><td colspan="7">Unable to load inventory.</td></tr>';
        showMessage(error.message, "error");
    }
}

function renderInventory() {
    inventoryBody.innerHTML = "";

    if (inventory.length === 0) {
        inventoryBody.innerHTML =
            '<tr><td colspan="7">No products found. Add your first product above.</td></tr>';
    }

    inventory.forEach((item) => {
        const row = document.createElement("tr");
        const stockValue = Number(item.quantity) * Number(item.price);

        const values = [
            item.id,
            item.product_name,
            item.category,
            item.quantity,
            formatCurrency(Number(item.price)),
            formatCurrency(stockValue)
        ];

        values.forEach((value) => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        const actionsCell = document.createElement("td");
        const actions = document.createElement("div");
        actions.className = "actions";

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.className = "edit";
        editButton.type = "button";
        editButton.addEventListener("click", () => editItem(item.id));

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.className = "danger";
        deleteButton.type = "button";
        deleteButton.addEventListener("click", () => deleteItem(item.id));

        actions.append(editButton, deleteButton);
        actionsCell.appendChild(actions);
        row.appendChild(actionsCell);

        inventoryBody.appendChild(row);
    });

    document.getElementById("total-products").textContent = inventory.length;

    const totalUnits = inventory.reduce(
        (total, item) => total + Number(item.quantity),
        0
    );

    const totalValue = inventory.reduce(
        (total, item) =>
            total + Number(item.quantity) * Number(item.price),
        0
    );

    document.getElementById("total-units").textContent = totalUnits;
    document.getElementById("total-value").textContent =
        formatCurrency(totalValue);
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const itemId = itemIdInput.value;

    const item = {
        product_name: productNameInput.value.trim(),
        category: categoryInput.value.trim(),
        quantity: Number(quantityInput.value),
        price: Number(priceInput.value)
    };

    if (
        !item.product_name ||
        !item.category ||
        !Number.isInteger(item.quantity) ||
        item.quantity < 0 ||
        !Number.isFinite(item.price) ||
        item.price < 0
    ) {
        showMessage("Please enter valid product details.", "error");
        return;
    }

    submitButton.disabled = true;

    try {
        if (itemId) {
            await request(`${API_URL}/${itemId}`, {
                method: "PUT",
                body: JSON.stringify(item)
            });

            showMessage("Product updated successfully.");
        } else {
            await request(API_URL, {
                method: "POST",
                body: JSON.stringify(item)
            });

            showMessage("Product added successfully.");
        }

        resetForm();
        await loadInventory();
    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        submitButton.disabled = false;
    }
});

function editItem(id) {
    const item = inventory.find((product) => product.id === id);

    if (!item) {
        showMessage("Product not found.", "error");
        return;
    }

    itemIdInput.value = item.id;
    productNameInput.value = item.product_name;
    categoryInput.value = item.category;
    quantityInput.value = item.quantity;
    priceInput.value = item.price;

    document.getElementById("form-title").textContent = "Edit Product";
    submitButton.textContent = "Update Product";
    cancelButton.hidden = false;

    form.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function deleteItem(id) {
    if (!confirm("Are you sure you want to delete this product?")) {
        return;
    }

    try {
        await request(`${API_URL}/${id}`, {
            method: "DELETE"
        });

        showMessage("Product deleted successfully.");
        await loadInventory();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function resetForm() {
    form.reset();
    itemIdInput.value = "";
    quantityInput.value = "0";
    priceInput.value = "0";

    document.getElementById("form-title").textContent = "Add New Product";
    submitButton.textContent = "Add Product";
    cancelButton.hidden = true;
}

cancelButton.addEventListener("click", resetForm);

document.getElementById("refresh-button").addEventListener(
    "click",
    loadInventory
);

loadInventory();