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
    var scrollPosition = document.documentElement.scrollTop || document.body.scrollTop;

    if (mainNav) {
        if (scrollPosition > 0) { // Check if navbar-shrink
            mainNav.classList.add('fixed-top');
            mainNav.classList.remove('vertical-height-100');
            navbarContent.classList.add('collapse', 'navbar-collapse');
            navbarContent.classList.remove('navbar-bottom');
            navbarToggler.classList.remove('d-none');
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

document.addEventListener('DOMContentLoaded', event => {

    // Navbar functionality
    navbarScroll();
    window.onscroll = navbarScroll;
    
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