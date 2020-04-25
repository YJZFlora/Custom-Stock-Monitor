var $TABLE = $('#table');
var $BTN = $('#export-btn');
var $EXPORT = $('#export');
var $SUBMIT = $('#submit-btn')

$('.table-add').click(function() {
    var $clone = $TABLE.find('tr.hide').clone(true).removeClass('hide table-line');
    $TABLE.find('table').append($clone);
});

$('.table-remove').click(function() {
    $(this).parents('tr').detach();
});

$('.table-up').click(function() {
    var $row = $(this).parents('tr');
    if ($row.index() === 1) return; // Don't go above the header
    $row.prev().before($row.get(0));
});

$('.table-down').click(function() {
    var $row = $(this).parents('tr');
    $row.next().after($row.get(0));
});

// A few jQuery helpers for exporting only
jQuery.fn.pop = [].pop;
jQuery.fn.shift = [].shift;

$BTN.click(function() {
    var $rows = $TABLE.find('tr:not(:hidden)');
    var headers = [];
    var data = [];

    if ($("#email-input").val() == "") {
        alert("Please enter your email id");
        return;
    }
    var reeamil = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,6})?$/;
    if (!reeamil.test($("#email-input").val())) {
        alert("Please enter valid email address");
        return;
    }

    var email = $("#email-input").val();
    data.push({ "Email": email })

    // Get the headers (add special header logic here)
    $($rows.shift()).find('th:not(:empty)').each(function() {
        // headers.push($(this).text().toLowerCase());
        headers.push($(this).text().split(" ")[0]);
    });

    // Turn all existing rows into a loopable array
    $rows.each(function() {
        var $td = $(this).find('td');
        var h = {};

        // Use the headers from earlier to name our hash keys
        headers.forEach(function(header, i) {
            if (i == 2) {
                h[header] = $td.eq(i).find('select').val();
            } else {
                h[header] = $td.eq(i).text();
            }
        });

        data.push(h);
    });

    var data_json = {
        "Email": data[0]["Email"],
        "Information": data.slice(1)
    }

    // Output the result
    $EXPORT.text(JSON.stringify(data_json));
});

$SUBMIT.click(function() {
    var $rows = $TABLE.find('tr:not(:hidden)');
    var headers = [];
    var data = [];

    if ($("#email-input").val() == "") {
        alert("Please enter your email id");
        return;
    }
    var reeamil = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,6})?$/;
    if (!reeamil.test($("#email-input").val())) {
        alert("Please enter valid email address");
        return;
    }

    var email = $("#email-input").val();
    data.push({ "Email": email })

    // Get the headers (add special header logic here)
    $($rows.shift()).find('th:not(:empty)').each(function() {
        // headers.push($(this).text().toLowerCase());
        headers.push($(this).text().split(" ")[0]);
    });

    // Turn all existing rows into a loopable array
    $rows.each(function() {
        var $td = $(this).find('td');
        var h = {};

        // Use the headers from earlier to name our hash keys
        headers.forEach(function(header, i) {
            if (i == 2) {
                h[header] = $td.eq(i).find('select').val();
            } else {
                h[header] = $td.eq(i).text();
            }
        });

        data.push(h);
    });

    var data_json = {
        "Email": data[0]["Email"],
        "Information": data.slice(1)
    }

    $.ajax({
        type: "POST",
        url: "https://nt2ytxwlx7.execute-api.us-east-2.amazonaws.com/test3/stock-monitor",
        dataType: "json",
        crossDomain: "true",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data_json),


        success: function() {
            // clear form and show a success message
            alert("Successfull");
            document.getElementById("contact-form").reset();
            location.reload();
        },
        error: function() {
            // show an error message
            alert("UnSuccessfull");
        }
    });
});