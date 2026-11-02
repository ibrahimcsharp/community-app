import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService } from '../services/auth.service';

/** The blue bar at the top. Shows different links for guests, users and admins. */
@Component({
  selector: 'app-navbar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.html',
})
export class Navbar {
  protected auth = inject(AuthService);

  /** On small screens the links fold into a menu button. */
  protected menuOpen = signal(false);

  toggleMenu(): void {
    this.menuOpen.update((open) => !open);
  }

  closeMenu(): void {
    this.menuOpen.set(false);
  }

  logout(): void {
    this.closeMenu();
    this.auth.logout();
  }
}
