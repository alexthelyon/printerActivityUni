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