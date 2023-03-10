Notification.requestPermission().then(() => {
    if (Notification.permission === "granted") {
        notifiable = true;
    }
});

let notifiable = false;

const ICON_LINK = "/static/image/logo.svg";

function show_notification(title, body) {
    if (!notifiable)
        return;

    return new Notification(title, {
        icon: ICON_LINK,
        body: body
    });
}
