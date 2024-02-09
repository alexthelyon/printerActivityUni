

// Hide plot3 (Bar Graph) when the page loads
window.onload = function() {
    var plot3 = document.getElementById('plot3');
    plot3.style.display = 'none';
};

function showPlot(plotId) {
    // Hide all plots
    var graphs = document.getElementsByClassName('changeable_graph');
    for (var i = 0; i < graphs.length; i++) {
        graphs[i].style.display = 'none';
    }
    // Show the selected plot
    document.getElementById(plotId).style.display = 'block';
}




// Adds shadow effect to the Flask printed graphs, as CSS wont do this effect on them.
document.querySelectorAll(".graph-container").forEach(function(container) {
    container.addEventListener("mouseenter", function() {
        this.style.boxShadow = "0px 0px 10px rgba(0, 0, 0, 0.5)";
    });

    container.addEventListener("mouseleave", function() {
        this.style.boxShadow = "none";
    });
});

document.querySelectorAll(".changeable_graph_container").forEach(function(container) {
    container.addEventListener("mouseenter", function() {
        this.style.boxShadow = "0px 0px 10px rgba(0, 0, 0, 0.5)";
    });

    container.addEventListener("mouseleave", function() {
        this.style.boxShadow = "none";
    });
});