// Add custom easing functions for smoother animations
$.easing.easeOutCubic = function (x, t, b, c, d) {
    return c*((t=t/d-1)*t*t + 1) + b;
};

$.easing.easeInCubic = function (x, t, b, c, d) {
    return c*(t/=d)*t*t + b;
};

let currentPanel = null;

async function showPanel(panelId) {
    console.log("Showing panel:", panelId);
    
    // Hide all panels first
    $('.panel').hide();
    
    if(currentPanel != null) {
        await hidePanel(currentPanel);
    }
    
    $('.panel-overlay').css("display", "flex");
    return new Promise((resolve) => {
        // Show overlay with smooth fade
        $(".panel-overlay")
            .css("opacity", 0)
            .animate({ opacity: 1 }, 300);
        
        // Show panel with smooth scale animation
        const $panel = $('#' + panelId);
        $panel.css({
            "display": "flex",
            "opacity": 0,
            "transform": "translate(-50%, -50%) scale(0.8)"
        }).animate(
            { opacity: 1 },
            {
                duration: 300,
                easing: "easeOutCubic",
                step: function(now, fx) {
                    if (fx.prop === 'opacity') {
                        const scale = 0.8 + (0.2 * now); // Scale from 0.8 to 1.0
                        $(this).css("transform", `translate(-50%, -50%) scale(${scale})`);
                    }
                },
                complete: function() {
                    $(this).css("transform", "translate(-50%, -50%) scale(1)");
                    currentPanel = panelId;
                    resolve();
                }
            }
        );
    });
}

async function hidePanel(panelId) {
    return new Promise((resolve) => {
        if (panelId && currentPanel === panelId) {
            const $panel = $('#' + panelId);
            // Hide panel with smooth scale animation
            $panel.animate(
                { opacity: 0 },
                {
                    duration: 250,
                    easing: "easeInCubic",
                    step: function(now, fx) {
                        if (fx.prop === 'opacity') {
                            const scale = 0.8 + (0.2 * now); // Scale from 1.0 to 0.8
                            $(this).css("transform", `translate(-50%, -50%) scale(${scale})`);
                        }
                    },
                    complete: function() {
                        $(this).hide();
                        // Hide overlay
                        $(".panel-overlay").animate({ opacity: 0 }, 200, function() {
                            $(this).hide();
                            $('.panel').hide();
                            currentPanel = null;
                            resolve();
                        });
                    }
                }
            );
        } else {
            // Hide all panels and overlay
            $('.panel').hide();
            $(".panel-overlay").animate({ opacity: 0 }, 200, function() {
                $(this).hide();
                currentPanel = null;
                resolve();
            });
        }
    });
}