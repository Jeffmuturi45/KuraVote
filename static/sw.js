// sw.js — KuraVote Service Worker
// Must be served from the root: /sw.js
// Handles incoming Web Push messages and shows OS-level notifications.

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});

// ── Receive a push and show an OS notification ───────────
self.addEventListener('push', event => {
  let data = { title: 'KuraVote', body: 'You have a new notification.', url: '/' };

  if (event.data) {
    try {
      data = JSON.parse(event.data.text());
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body:    data.body,
    icon:    '/static/img/icon-192.png',  // add a 192×192 PNG to static/img/
    badge:   '/static/img/badge-72.png',  // small monochrome 72×72 PNG
    vibrate: [100, 50, 100],
    data:    { url: data.url || '/' },
    actions: [
      { action: 'open',    title: 'Open KuraVote' },
      { action: 'dismiss', title: 'Dismiss' },
    ],
    tag:     'kuravote-notification',   // replaces previous notification of same tag
    renotify: true,
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// ── Tapping the notification opens the app ───────────────
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'dismiss') return;

  const url = (event.notification.data && event.notification.data.url)
    ? event.notification.data.url
    : '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // If app is already open, focus it
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(url);
            return client.focus();
          }
        }
        // Otherwise open a new window
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});