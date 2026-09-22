document.addEventListener(
    "DOMContentLoaded",
    () => {

        const seats =
            document.querySelectorAll(
                ".seat.available"
            );

        const selectedSeats =
            document.getElementById(
                "selected-seats"
            );

        const totalPrice =
            document.getElementById(
                "total-price"
            );

        const continueButton =
            document.getElementById(
                "continue-button"
            );


        let selected = [];


        // =========================================
        // SELECT / UNSELECT SEAT
        // =========================================

        seats.forEach(seat => {

            seat.addEventListener(
                "click",
                () => {

                    const seatId =
                        seat.dataset.seatId;

                    const seatName =
                        seat.dataset.seatName;

                    const price =
                        Number(
                            seat.dataset.price
                        );


                    const existingIndex =
                        selected.findIndex(
                            item =>
                                item.id === seatId
                        );


                    // UNSELECT

                    if (
                        existingIndex !== -1
                    ) {

                        selected.splice(
                            existingIndex,
                            1
                        );

                        seat.classList.remove(
                            "selected"
                        );

                    }

                    // SELECT

                    else {

                        selected.push({

                            id: seatId,

                            name: seatName,

                            price: price

                        });

                        seat.classList.add(
                            "selected"
                        );

                    }


                    updateSummary();

                }

            );

        });


        // =========================================
        // UPDATE SUMMARY
        // =========================================

        function updateSummary() {

            if (
                selected.length === 0
            ) {

                selectedSeats.textContent =
                    "None";

                totalPrice.textContent =
                    "0";

                continueButton.disabled =
                    true;

                return;

            }


            selectedSeats.textContent =
                selected
                    .map(
                        seat => seat.name
                    )
                    .join(", ");


            const total =
                selected.reduce(
                    (sum, seat) =>
                        sum + seat.price,
                    0
                );


            totalPrice.textContent =
                total;


            continueButton.disabled =
                false;

        }


        // =========================================
        // CONTINUE TO PAYMENT
        // =========================================

        continueButton.addEventListener(
            "click",
            async () => {

                if (
                    selected.length === 0
                ) {
                    return;
                }


                continueButton.disabled =
                    true;

                continueButton.textContent =
                    "Holding Seats...";


                try {

                    const response =
                        await fetch(
                            "/booking/hold-seats",
                            {

                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({

                                    show_id:
                                        SHOW_ID,

                                    seat_ids:
                                        selected.map(
                                            seat =>
                                                Number(
                                                    seat.id
                                                )
                                        )

                                })

                            }
                        );


                    const data =
                        await response.json();


                    if (
                        response.ok &&
                        data.success
                    ) {

                        window.location.href =
                            data.redirect_url;

                        return;

                    }


                    alert(
                        data.message ||
                        "Some seats are no longer available."
                    );


                    // Reload because another
                    // user may have taken the seat

                    window.location.reload();


                } catch (error) {

                    console.error(error);


                    alert(
                        "Unable to hold seats. Please try again."
                    );


                    continueButton.disabled =
                        false;

                    continueButton.textContent =
                        "Continue to Payment →";

                }

            }
        );

    }
);