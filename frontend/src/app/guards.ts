import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from './services/auth.service';

// Guards decide if a page may open. They are attached to routes in app.routes.ts.
// (They only protect the screens. The real security check happens in Django.)

/** Page needs a logged-in user, otherwise go to /login. */
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isLoggedIn() ? true : inject(Router).createUrlTree(['/login']);
};

/** Page needs an admin, otherwise go to /community. */
export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isAdmin() ? true : inject(Router).createUrlTree(['/community']);
};
