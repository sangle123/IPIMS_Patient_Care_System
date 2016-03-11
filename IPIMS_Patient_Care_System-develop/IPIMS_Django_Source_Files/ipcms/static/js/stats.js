$(document).ready(function(){
var ctx = $("#mycanvas").get(0).getContext("2d");

var data = [
    {
        value: {{num_males}},
        color: "cornflowerblue",
        highlight: "lightskyblue",
        label: "% of Males"
    },
    {
        value: {{num_females}},
        color: "lightgreen",
        highlight: "yellowgreen",
        label: "% of Females"
    },
    {
        value: {{num_other}},
        color: "orange",
        highlight: "darkorange",
        label: "% of Other"
    },
    {
        value: {{num_PNTS}},
        color: "pink",
        highlight: "darkorange",
        label: "% of Prefer Not To Say"
    },

];

var chart = new Chart(ctx).Doughnut(data);
});