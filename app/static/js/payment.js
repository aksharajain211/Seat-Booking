document.addEventListener("DOMContentLoaded", () => {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const paymentForm =
        document.getElementById("payment-form");

    const payButton =
        document.getElementById("pay-button");

    const paymentMessage =
        document.getElementById("payment-message");

    const countdown =
        document.getElementById("countdown");

    const cardDetails =
        document.getElementById("card-details");

    const cardNumber =
        document.getElementById("card-number");

    const expiry =
        document.getElementById("expiry");

    const cvv =
        document.getElementById("cvv");

    const paymentMethods =
        document.querySelectorAll(
            'input[name="payment_method"]'
        );


    // =====================================================
    // CHECK PAYMENT PAGE
    // =====================================================

    if (!paymentForm) {
        return;
    }


    // =====================================================
    // BOOKING INFORMATION
    // =====================================================

    const bookingId =
        paymentForm.dataset.bookingId;

    const holdUntil =
        paymentForm.dataset.holdUntil;


    // =====================================================
    // PAYMENT METHOD SELECTION
    // =====================================================

    paymentMethods.forEach(method => {

        method.addEventListener("change", () => {

            // Remove selected class
            // from all methods

            paymentMethods.forEach(item => {

                const container =
                    item.closest(".payment-method");

                if (container) {
                    container.classList.remove("selected");
                }

            });


            // Add selected class
            // to current method

            const selectedContainer =
                method.closest(".payment-method");

            if (selectedContainer) {
                selectedContainer.classList.add("selected");
            }


            // Show / hide card details

            if (method.value === "CARD") {

                if (cardDetails) {
                    cardDetails.style.display = "block";
                }

            } else {

                if (cardDetails) {
                    cardDetails.style.display = "none";
                }

            }

        });

    });


    // =====================================================
    // CARD NUMBER FORMATTING
    // =====================================================

    if (cardNumber) {

        cardNumber.addEventListener("input", () => {

            let value =
                cardNumber.value
                    .replace(/\D/g, "")
                    .substring(0, 16);


            const groups =
                value.match(/.{1,4}/g);


            cardNumber.value =
                groups
                    ? groups.join(" ")
                    : "";

        });

    }


    // =====================================================
    // EXPIRY FORMATTING
    // =====================================================

    if (expiry) {

        expiry.addEventListener("input", () => {

            let value =
                expiry.value
                    .replace(/\D/g, "")
                    .substring(0, 4);


            if (value.length > 2) {

                value =
                    value.substring(0, 2)
                    + "/"
                    + value.substring(2);

            }


            expiry.value = value;

        });

    }


    // =====================================================
    // CVV FORMATTING
    // =====================================================

    if (cvv) {

        cvv.addEventListener("input", () => {

            cvv.value =
                cvv.value
                    .replace(/\D/g, "")
                    .substring(0, 3);

        });

    }


    // =====================================================
    // COUNTDOWN TIMER
    // =====================================================

    function startCountdown() {

        if (!countdown || !holdUntil) {
            return;
        }


        /*
         * hold_until is sent from Flask as UTC.
         *
         * Example:
         * 2026-09-22T09:20:00Z
         *
         * The Z tells JavaScript that this is UTC.
         */

        const endTime =
            new Date(holdUntil).getTime();


        if (isNaN(endTime)) {

            console.error(
                "Invalid hold_until:",
                holdUntil
            );

            countdown.textContent = "05:00";

            return;
        }


        let expired = false;


        function updateTimer() {

            const now =
                Date.now();


            const remaining =
                endTime - now;


            // =================================================
            // TIMER EXPIRED
            // =================================================

            if (remaining <= 0) {

                if (expired) {
                    return;
                }

                expired = true;


                countdown.textContent =
                    "00:00";


                countdown.classList.add(
                    "expired"
                );


                if (payButton) {

                    payButton.disabled = true;

                    payButton.textContent =
                        "Seat Hold Expired";

                }


                showMessage(
                    "Your seat hold has expired. Please select your seats again.",
                    "error"
                );


                /*
                 * Redirect only AFTER the hold has actually
                 * expired.
                 */

                setTimeout(() => {

                    window.location.href =
                        "/movies/";

                }, 2500);


                return;
            }


            // =================================================
            // CALCULATE TIME
            // =================================================

            const minutes =
                Math.floor(
                    remaining / 60000
                );


            const seconds =
                Math.floor(
                    (remaining % 60000) / 1000
                );


            countdown.textContent =
                String(minutes).padStart(2, "0")
                + ":"
                + String(seconds).padStart(2, "0");


            // =================================================
            // WARNING
            // =================================================

            if (remaining <= 60000) {

                countdown.classList.add(
                    "warning"
                );

            }

        }


        // Run immediately

        updateTimer();


        // Update every second

        const timer =
            setInterval(() => {

                if (expired) {

                    clearInterval(timer);

                    return;
                }


                updateTimer();


                if (Date.now() >= endTime) {

                    clearInterval(timer);

                }

            }, 1000);

    }


    startCountdown();


    // =====================================================
    // PAYMENT VALIDATION
    // =====================================================

    function validatePayment() {

        const selectedMethod =
            document.querySelector(
                'input[name="payment_method"]:checked'
            );


        if (!selectedMethod) {

            showMessage(
                "Please select a payment method.",
                "error"
            );

            return false;
        }


        // =================================================
        // CARD VALIDATION
        // =================================================

        if (selectedMethod.value === "CARD") {

            const number =
                cardNumber
                    ? cardNumber.value
                        .replace(/\s/g, "")
                    : "";


            const expiryValue =
                expiry
                    ? expiry.value
                    : "";


            const cvvValue =
                cvv
                    ? cvv.value
                    : "";


            if (number.length !== 16) {

                showMessage(
                    "Please enter a valid 16-digit card number.",
                    "error"
                );

                return false;
            }


            if (!/^\d{2}\/\d{2}$/.test(expiryValue)) {

                showMessage(
                    "Please enter expiry in MM/YY format.",
                    "error"
                );

                return false;
            }


            if (cvvValue.length !== 3) {

                showMessage(
                    "Please enter a valid 3-digit CVV.",
                    "error"
                );

                return false;
            }

        }


        return true;

    }


    // =====================================================
    // PAYMENT SUBMISSION
    // =====================================================

    paymentForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            // Validate

            if (!validatePayment()) {
                return;
            }


            // Prevent double payment

            payButton.disabled = true;

            payButton.textContent =
                "Processing Payment...";


            showMessage(
                "Processing your payment...",
                "processing"
            );


            const selectedMethod =
                document.querySelector(
                    'input[name="payment_method"]:checked'
                );


            try {

                /*
                 * IMPORTANT:
                 *
                 * This endpoint matches:
                 *
                 * /payment/confirm/<booking_id>
                 */

                const response =
                    await fetch(
                        `/payment/confirm/${bookingId}`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                payment_method:
                                    selectedMethod.value

                            })

                        }
                    );


                const data =
                    await response.json();


                // =================================================
                // SUCCESS
                // =================================================

                if (
                    response.ok &&
                    data.success
                ) {

                    showMessage(
                        "Payment successful! Redirecting...",
                        "success"
                    );


                    payButton.textContent =
                        "Payment Successful ✓";


                    setTimeout(() => {

                        window.location.href =
                            data.redirect_url;

                    }, 800);


                    return;
                }


                // =================================================
                // PAYMENT FAILED
                // =================================================

                showMessage(
                    data.message ||
                    "Payment failed. Please try again.",
                    "error"
                );


                payButton.disabled = false;

                payButton.textContent =
                    "Pay ₹" +
                    document
                        .querySelector(".pay-button")
                        .textContent
                        .replace("Pay ₹", "");

            } catch (error) {

                console.error(
                    "Payment error:",
                    error
                );


                showMessage(
                    "Unable to connect to the payment server.",
                    "error"
                );


                payButton.disabled = false;

                payButton.textContent =
                    "Try Again";

            }

        }
    );


    // =====================================================
    // MESSAGE FUNCTION
    // =====================================================

    function showMessage(
        message,
        type
    ) {

        if (!paymentMessage) {
            return;
        }


        paymentMessage.textContent =
            message;


        paymentMessage.className =
            "payment-message " + type;

    }

});