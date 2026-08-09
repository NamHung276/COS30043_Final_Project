<template>
  <footer class="gd-footer mt-auto py-5 bg-dark text-muted">
    <div class="container">
      <div class="row gy-4 border-bottom border-secondary border-opacity-25 pb-4 mb-4">
        <!-- Brand and About -->
        <div class="col-lg-4 col-md-6">
          <div class="d-flex align-items-center gap-2 mb-3">
            <i class="bi bi-controller fs-4 text-primary"></i>
            <h5 class="text-white mb-0 fw-bold">GameHub</h5>
          </div>
          <p class="small mb-3">
            Your destination for discovering, tracking, and exploring the vast universe of video games. We aggregate data from top sources like RAWG, Steam, and IsThereAnyDeal.
          </p>
          <div class="d-flex gap-3 fs-5">
            <a href="#" class="text-muted text-decoration-none hover-white" aria-label="X (formerly Twitter)"><i class="bi bi-twitter-x"></i></a>
            <a href="#" class="text-muted text-decoration-none hover-white" aria-label="Discord"><i class="bi bi-discord"></i></a>
            <a href="#" class="text-muted text-decoration-none hover-white" aria-label="YouTube"><i class="bi bi-youtube"></i></a>
            <a href="#" class="text-muted text-decoration-none hover-white" aria-label="GitHub"><i class="bi bi-github"></i></a>
          </div>
        </div>

        <!-- Links -->
        <div class="col-lg-2 col-md-3 col-6">
          <h6 class="text-white mb-3 fw-bold">Games</h6>
          <ul class="list-unstyled small d-flex flex-column gap-2">
            <li><router-link to="/deals" class="text-muted text-decoration-none hover-white">Deals & Offers</router-link></li>
            <li><router-link to="/free-to-play" class="text-muted text-decoration-none hover-white">Free To Play</router-link></li>
            <li><router-link to="/paid-games" class="text-muted text-decoration-none hover-white">Premium Games</router-link></li>
            <li><router-link to="/library" class="text-muted text-decoration-none hover-white">My Library</router-link></li>
          </ul>
        </div>

        <div class="col-lg-2 col-md-3 col-6">
          <h6 class="text-white mb-3 fw-bold">Discover</h6>
          <ul class="list-unstyled small d-flex flex-column gap-2">
            <li><router-link to="/news" class="text-muted text-decoration-none hover-white">News & Updates</router-link></li>
            <li><router-link to="/converter" class="text-muted text-decoration-none hover-white">Currency Converter</router-link></li>
            <li><router-link to="/profile" class="text-muted text-decoration-none hover-white">My Profile</router-link></li>
            <li><router-link to="/favorites" class="text-muted text-decoration-none hover-white">Wishlist</router-link></li>
          </ul>
        </div>

        <!-- Trust & Security -->
        <div class="col-lg-4 col-md-12">
          <h6 class="text-white mb-3 fw-bold">Secure Checkout</h6>
          <p class="small mb-3">We use 256-bit SSL encryption to ensure your transactions are safe and secure.</p>
          <div class="d-flex gap-2 mb-4 fs-3 text-secondary">
            <i class="bi bi-cc-paypal" title="PayPal"></i>
            <i class="bi bi-cc-visa" title="Visa"></i>
            <i class="bi bi-cc-mastercard" title="Mastercard"></i>
            <i class="bi bi-cc-stripe" title="Stripe"></i>
          </div>
        </div>
      </div>

      <!-- Legal & Copyright -->
      <div class="row align-items-center">
        <div class="col-md-8 small">
          <div class="d-flex flex-wrap gap-3 mb-2">
            <router-link to="/about" class="text-muted text-decoration-none hover-white">About</router-link>
          </div>
          <p class="mb-0">&copy; {{ new Date().getFullYear() }} GameHub Inc. All rights reserved. All trademarks are property of their respective owners in the US and other countries.</p>
          <p class="mb-0 mt-1 opacity-50" style="font-size: 0.75rem;">Data provided by RAWG Video Games Database API and CheapShark.</p>
        </div>
        
        <div class="col-md-4 text-md-end mt-3 mt-md-0 d-flex justify-content-md-end align-items-center gap-3">
           <div class="gd-age-rating border border-secondary p-1 rounded d-inline-block text-center" style="width: 45px; height: 60px; background: #000;">
             <div class="bg-white text-dark fw-bold fs-3 lh-1 pt-1" style="height: 35px;">T</div>
             <div class="text-white fw-bold lh-1 mt-1" style="font-size: 10px;">ESRB</div>
           </div>
           <div class="small text-start lh-sm" style="max-width: 120px;">
             Teen<br>Violence<br>Blood
           </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.gd-footer {
  background-color: var(--bg-dark, #0d0f12) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.hover-white {
  transition: color 0.2s ease;
}

.hover-white:hover {
  color: var(--text-primary, #ffffff) !important;
}

.gd-footer-logo {
  filter: drop-shadow(0 0 5px rgba(255,255,255,0.2));
}

.gd-age-rating {
  user-select: none;
}
</style>
