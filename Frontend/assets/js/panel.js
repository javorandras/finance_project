let currentPanel = null;

async function showPanel(panelId) {
    console.log("Showing panel:", panelId);
    if(currentPanel != null) {
        await hidePanel(currentPanel);
    }
    $('.panel-overlay').css("display", "block");
    return new Promise((resolve) => {
        // Set initial styles before animation
        $(".panel-overlay")
            .css({
                "display": "block",
                "opacity": 0,
                "backdrop-filter": "blur(8px)"
            })
            .animate(
                { opacity: 1 },
                {
                    duration: 200,
                    complete: function() {
                        currentPanel = panelId;
                        $('#' + panelId)
                            .css("display", "block")
                            .hide()
                            .fadeIn(200, () => resolve());
                    }
                }
            );
    });
}
async function hidePanel(panelId) {
    return new Promise((resolve) => {
        if (panelId && currentPanel === panelId) {
            $('#' + panelId).fadeOut(200, () => {
                $(".panel-overlay").fadeOut(200, () => {
                    currentPanel = null;
                    resolve();
                });
            });
        } else {
            $(".panel-overlay").fadeOut(200, () => resolve());
        }
    });
}