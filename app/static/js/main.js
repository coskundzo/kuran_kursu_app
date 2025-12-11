// Custom JavaScript for E-Kuran Kursu

$(document).ready(function () {
    // Alerts will stay visible until manually dismissed by user
    // (No auto-hide timeout)

    // Confirm delete actions
    $('.btn-delete').on('click', function (e) {
        if (!confirm('Bu kaydı silmek istediğinizden emin misiniz?')) {
            e.preventDefault();
        }
    });

    // Phone number formatting
    $('input[type="tel"]').on('input', function () {
        let value = $(this).val().replace(/\D/g, '');
        if (value.length > 10) {
            value = value.substr(0, 10);
        }
        $(this).val(value);
    });

    // TC Kimlik No validation
    $('input[name="tc"]').on('input', function () {
        let value = $(this).val().replace(/\D/g, '');
        if (value.length > 11) {
            value = value.substr(0, 11);
        }
        $(this).val(value);
    });

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// AJAX form submission helper
function submitFormAjax(formId, successCallback) {
    $(`#${formId}`).on('submit', function (e) {
        e.preventDefault();

        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (response) {
                if (successCallback) {
                    successCallback(response);
                }
            },
            error: function (xhr) {
                alert('Bir hata oluştu: ' + xhr.responseText);
            }
        });
    });
}

// Show loading spinner
function showLoading() {
    $('body').append('<div class="loading-overlay"><div class="spinner-border text-primary" role="status"></div></div>');
}

// Hide loading spinner
function hideLoading() {
    $('.loading-overlay').remove();
}

// Format date to DD.MM.YYYY
function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
}

// Format phone number
function formatPhone(phone) {
    if (!phone) return '';
    phone = phone.replace(/\D/g, '');
    if (phone.length === 10) {
        return `(${phone.substr(0, 3)}) ${phone.substr(3, 3)} ${phone.substr(6, 2)} ${phone.substr(8, 2)}`;
    }
    return phone;
}
