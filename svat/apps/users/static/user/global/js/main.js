$(document).ready(function () {
  // Init category
  let url = `/${window.location.pathname.split("/")[1]}/categories`;
  $.ajax({
    type: "GET",
    url,
    success: function (res) {
      // Product category
      let product_categories = JSON.parse(res["product_categories"]);
      result = `<li><a href="/product">${window.location.pathname.split("/")[1] == "en" ? "All" : "Tất cả"}</a></li>`;
      for (let item in product_categories) {
        let name = product_categories[item]["fields"][`name_${window.location.pathname.split("/")[1]}` ];
        let url = `/product?category=${product_categories[item].pk}`;
        result += `<li><a href="${url}">${name}</a></li>`;
      }
      $(".all-category").html(result);
  
      // Article Product mobile
      if (res["article_categories"]) {
        let article_categories = JSON.parse(res["article_categories"]);
        result = `<li><a href="/articles">${window.location.pathname.split("/")[1] == "en" ? "All" : "Tất cả"}</a></li>`;
        for (let item in article_categories) {
          let name = article_categories[item]["fields"][`name_${window.location.pathname.split("/")[1]}` ];
          let url = `/articles?category=${article_categories[item].pk}`;
          result += `<li><a href="${url}">${name}</a></li>`;
        }
        $(".all-category-article").html(result);
      }

    },
  });

  // Init shopping cart
  url = `/${window.location.pathname.split("/")[1]}/get-shopping-cart`;
  $.ajax({
    type: "GET",
    url,
    success: function (res) {
      $('.total-cart-span').html(res.total)
    },
  });


  // Handle add to cart of product components
  $(".add-to-card-component-btn").click(function () {
    const data = {
      product_id: $(this).data('id'),
      product_model_id: $(this).data('model-id'),
      quantity: 1,
    };

    const url = `/${window.location.pathname.split("/")[1]}/add-product-to-cart`;
    $.ajax({
      url,
      type: "POST",
      headers: {
        "X-CSRFTOKEN": $("[name=csrfmiddlewaretoken]").val(),
      },
      dataType: "json",
      processData: false,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(data),
      success: function (data) {
        if (data.success) {
          toastr.success(data.message);
          $('.total-cart-span').html(data.data.total)
        } else {
          toastr.warning(data.message);
        }
      },
    });
  });

  $('.hero__categories__all').on('click', function() {
      $(this).parent().find('ul').slideToggle(400);
  });

  $('.article-component').click(function() {
    window.location= '/article/' + $(this).find('input').val()
  })
  $('.product-component').click(function(e) {
    if ($(e.target).hasClass("fa-shopping-cart") || $(e.target).hasClass('add-to-card-component-btn') ) return;
    window.location= '/product/' + $(this).find('input').val()
  })

  
});
