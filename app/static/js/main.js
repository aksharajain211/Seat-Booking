document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // FLASH MESSAGES
    // ==========================================

    const flashMessages =
        document.querySelectorAll(".flash");

    flashMessages.forEach(message => {

        setTimeout(() => {

            message.style.opacity = "0";

            setTimeout(() => {
                message.remove();
            }, 500);

        }, 3000);

    });


    // ==========================================
    // MOVIE SEARCH
    // ==========================================

    const searchInput =
        document.getElementById("movie-search");

    const movieCards =
        document.querySelectorAll(".movie-card");

    const noMovies =
        document.getElementById("no-movies");

    const movieCount =
        document.getElementById("movie-count");


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterMovies
        );

    }


    // ==========================================
    // GENRE FILTER
    // ==========================================

    const filterButtons =
        document.querySelectorAll(
            ".filter-btn"
        );


    filterButtons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                filterButtons.forEach(btn => {

                    btn.classList.remove(
                        "active"
                    );

                });


                button.classList.add(
                    "active"
                );


                filterMovies();

            }
        );

    });


    // ==========================================
    // FILTER FUNCTION
    // ==========================================

    function filterMovies() {

        const searchText =
            searchInput
                ? searchInput.value
                    .toLowerCase()
                    .trim()
                : "";


        const activeFilter =
            document.querySelector(
                ".filter-btn.active"
            );


        const genre =
            activeFilter
                ? activeFilter.dataset.filter
                : "all";


        let visibleCount = 0;


        movieCards.forEach(card => {

            const title =
                (
                    card.dataset.title || ""
                ).toLowerCase();


            const cardGenre =
                (
                    card.dataset.genre || ""
                ).toLowerCase();


            const matchesSearch =
                title.includes(
                    searchText
                );


            const matchesGenre =
                genre === "all" ||
                cardGenre ===
                    genre.toLowerCase();


            if (
                matchesSearch &&
                matchesGenre
            ) {

                card.style.display =
                    "";

                visibleCount++;

            } else {

                card.style.display =
                    "none";

            }

        });


        if (noMovies) {

            noMovies.style.display =
                visibleCount === 0
                    ? "block"
                    : "none";

        }


        if (movieCount) {

            movieCount.textContent =
                `${visibleCount} ${
                    visibleCount === 1
                        ? "movie"
                        : "movies"
                }`;

        }

    }


    // ==========================================
    // PREVENT DOUBLE FORM SUBMISSION
    // ==========================================

    document
        .querySelectorAll("form")
        .forEach(form => {

            form.addEventListener(
                "submit",
                () => {

                    const button =
                        form.querySelector(
                            'button[type="submit"]'
                        );


                    if (button) {

                        button.disabled =
                            true;

                    }

                }
            );

        });

});