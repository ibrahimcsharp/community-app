import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { Navbar } from './navbar/navbar';

/** The outer frame of every page: the navbar on top, the current page below. */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Navbar],
  templateUrl: './app.html',
})
export class App {}
