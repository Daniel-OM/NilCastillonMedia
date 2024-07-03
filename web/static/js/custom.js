function generateToTop () {
    if ( !window.xMode ) {
        let node = document.createElement( 'div' );
        node.className = 'to-top fa-angle-up';
        document.body.appendChild( node );

        node.addEventListener( 'mousedown', function () {
            this.classList.add( 'active' );

            $( 'html, body' ).stop().animate( { scrollTop:0 }, 500, 'swing', (function () {
                this.classList.remove( 'active' );
            }).bind( this ));
        });

        document.addEventListener( 'scroll', function () {
            if ( window.scrollY > window.innerHeight ) node.classList.add( 'show' );
            else node.classList.remove( 'show' );
        });
    }
}


window.addEventListener( 'load', function () {
    generateToTop();
});




// Navbar management
function navbarScroll() { 
    let mainNav = document.getElementById('mainNav');
    let brandContainer = document.querySelector(".navbar-brand-container");
    let navbarContent = document.getElementById('navbarContent');
    let navbarToggler = document.getElementById('navbarToggler');
    let typed_text = document.getElementById('typed_text');
    var scrollPosition = document.documentElement.scrollTop || document.body.scrollTop;

    if (mainNav) {
        if (scrollPosition > 0) { // Check if navbar-shrink
            mainNav.classList.add('fixed-top');
            mainNav.classList.remove('vertical-height-100');
            navbarContent.classList.add('collapse', 'navbar-collapse');
            navbarContent.classList.remove('navbar-bottom');
            navbarToggler.classList.remove('d-none');
            typed_text.classList.add('d-none');
            if (window.innerWidth >= 992) {
                brandContainer.classList.add('hidden-up');
            }
        } 
        else {
            mainNav.classList.remove('fixed-top');
            mainNav.classList.add('vertical-height-100');
            navbarContent.classList.remove('collapse', 'navbar-collapse');
            navbarContent.classList.add('navbar-bottom');
            brandContainer.classList.remove('hidden-up');
            navbarToggler.classList.add('d-none');
            typed_text.classList.remove('d-none');
        }

        var nav_links = document.querySelectorAll(".nav-link");
        for (let l of nav_links) {
            if (l.href.includes('#')) {
                let section = document.getElementById(l.href.split('#').at(-1));
                if (section.getBoundingClientRect().top <= 150 & 150 <= section.getBoundingClientRect().bottom) {
                    l.classList.add('active');
                } else {
                    l.classList.remove('active');
                }
            }
        }
    }

};

function topFunction(value=0) {
    window.removeEventListener("scroll", fixNav, true);
    document.body.scrollTop = value; // For Safari
    document.documentElement.scrollTop = value; // For Chrome, Firefox, IE and Opera
    window.addEventListener('scroll', fixNav);
}

let prev_pos = window.scrollY;
function fixNav() {
    let mainNav = document.getElementById('mainNav');
    let brandContainer = document.querySelector(".navbar-brand-container");
    let navbarContent = document.getElementById('navbarContent');
    let navbarToggler = document.getElementById('navbarToggler');
    let typed_text = document.getElementById('typed_text');

    if (navbarContent) {
        console.log(navbarContent.getBoundingClientRect().top);
        if (window.innerWidth < 992) {
            console.log(window.scrollY, navbarContent.offsetTop, prev_pos)
            if (window.scrollY > navbarContent.offsetTop & prev_pos < navbarContent.offsetTop) {
                mainNav.classList.add('fixed-top');
                mainNav.classList.remove('vertical-height-100');
                navbarToggler.classList.remove('d-none');
                navbarContent.classList.add('collapse', 'navbar-collapse');
                typed_text.classList.add('d-none');

                topFunction(1);
    
            } else if (window.scrollY <= 0) {
                mainNav.classList.remove('fixed-top');
                mainNav.classList.add('vertical-height-100');
                navbarToggler.classList.add('d-none');
                navbarContent.classList.remove('collapse', 'navbar-collapse');
                typed_text.classList.remove('d-none');
            }
            prev_pos = window.scrollY;
        } else {
            if (window.scrollY <= mainNav.getBoundingClientRect().bottom) {
                navbarContent.classList.remove('fixed-top');
            } else if (window.scrollY > navbarContent.offsetTop) {
                navbarContent.classList.add('fixed-top');
            }

        }
    }

    if (mainNav) {
        var nav_links = document.querySelectorAll(".nav-link");
        for (let l of nav_links) {
            if (l.href.includes('#')) {
                let section = document.getElementById(l.href.split('#').at(-1));
                if (section.getBoundingClientRect().top <= 150 & 150 <= section.getBoundingClientRect().bottom) {
                    l.classList.add('active');
                } else {
                    l.classList.remove('active');
                }
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', event => {

    // Navbar functionality
    fixNav();
    // window.onscroll = navbarScroll;
    window.addEventListener('scroll', fixNav);
    
    const navbarToggler = document.getElementById('navbarToggler');
    navbarToggler.addEventListener('click', function () {
        navbarToggler.click();
    });
    document.querySelectorAll('#navbarContent .nav-item').forEach((l) => {
        l.addEventListener('click', () => {
            if (window.innerWidth < 992 & !navbarToggler.classList.contains('collapsed')) {
                navbarToggler.click();
            }
        });
    });

    document.addEventListener('scroll', () => {
        if (window.innerWidth < 992 & !navbarToggler.classList.contains('collapsed')) {
            navbarToggler.click();
        }
    });

});




function gallery() {
    const gallery = document.querySelector('.gallery');
    const items = document.querySelectorAll('.gallery-item');

    let index = 0;

    setInterval(() => {
        gallery.style.transform = `translateX(${-index * 100}vw)`;
        index = (index + 1) % items.length;
    }, 5000);
}


document.addEventListener('DOMContentLoaded', () => {

    document.getElementById('copyright').innerHTML = `
    Copyright © 2023-${new Date().getFullYear()} Nil Castillon Media. Created by <a href="https://onemade.es">OneMade</a>
    `;

    // Para esconder el menu
    document.querySelector('.toggle').addEventListener('click', () => {
        document.querySelector('.navigation').classList.toggle('active');
        document.querySelector('.main').classList.toggle('active');
    });

    document.querySelectorAll('.navigation a').forEach( (item) => {
        item.addEventListener('click', () => {
            if (window.innerWidth <= 1076) {
                document.querySelector('.navigation').classList.toggle('active');
                document.querySelector('.main').classList.toggle('active');
            }
        });
    });

    gallery();
});