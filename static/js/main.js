var request

/* Called by clicking gap elements.
  * Submits ajax request and sets up future onclick events */
function show_spaceinfo(gap_ele) {
  var spaceID = gap_ele.id.split("-")[1]
  ajax_spaceinfo(spaceID)

  gap_ele.onclick = function() {
    var jgap_ele = $(gap_ele)
    jgap_ele.children(".spaceinfo").slideToggle("300")
  }
}

function show_results(){
  setTimeout(function search_results() {
  var index = document.form.campus.selectedIndex
  var building = document.form.building.value
  if (building == ""){
    postdata = "campus=" + campus[index].value
  }
  else {
    postdata = "campus=" + campus[index].value + "&search=" + building
  }
  request = $.ajax({
    url: "/search",
    type: "GET",
    data: postdata,
    success: function(response) {
      var gap = document.getElementById('gaps')
      gap.innerHTML = response
    },
    error: function(response) {
    }
  })
}
,500);
}

/* Submit AJAX request for retrieving the spaceinfo div element */
function ajax_spaceinfo(spaceID) {
  postdata = "spaceID=" + spaceID

  request = $.ajax({
    url: "/spaceinfo",
    type: "GET",
    data: postdata,
    success: function(response) {
      var gap = $("#gap-" + spaceID)
      gap.append(response)
    },
    error: function(response) {
      alert('failure: ' + response)
    }
  })
}

$(function() {
    return $('article#filter a').each(function(index, link) {
      var $link = $(link)
      var href = $link.attr('href')
      var URI = document.location.pathname
      if (href === URI) {
        $link.addClass('current')
      } else {$link.removeClass('current')}
    })
  })

