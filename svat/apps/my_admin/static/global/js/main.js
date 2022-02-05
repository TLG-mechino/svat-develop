$(document).ready(function() {
  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })        
  // init badge don hang
  let url = 'getMessageInProgress'
  $.ajax({
    url,
    type: "GET",
    success(res) {
      if (res.total > 0) {
        $('.badge-message').html(res.total)
        $('.badge-message').removeClass('d-none')
      } else {
        $('.badge-message').addClass('d-none')
      }

    }
  })


  url = 'getOrderInProgress'
  $.ajax({
    url,
    type: "GET",
    success(res) {
      if (res.total > 0) {
        $('.badge-order').html(res.total)
        $('.badge-order').removeClass('d-none')
      } else {
        $('.badge-order').addClass('d-none')
      }

    }
  })

})