function capturarInformacionUsuario(idEditar) {
  ////////////////////////////////////////////////
  //////////////////  PREGUNTA 3  ////////////////
  ///////////////////////////////////////////////
  console.log(idEditar);
  fetch(`/conseguirInfoUsuario?idEditar=${idEditar}`)
    .then((response) => response.json())
    .then((data) => {
      let nombreUsuarioDetalle = document.getElementById(
        "nombreUsuarioDetalle"
      );
      let apellidoUsuarioDetalle = document.getElementById(
        "apellidoUsuarioDetalle"
      );
      let tipoUsuarioDetalle = document.getElementById("tipoUsuarioDetalle");
      let emailUsuarioDetalle = document.getElementById("emailUsuarioDetalle");
      let profesionUsuarioDetalle = document.getElementById(
        "profesionUsuarioDetalle"
      );
      let nroCelularDetalle = document.getElementById("nroCelularDetalle");
      let indUsuario = document.getElementById("indUsuario");

      nombreUsuarioDetalle.value = data.nombreUsuario;
      apellidoUsuarioDetalle.value = data.apellidoUsuario;
      tipoUsuarioDetalle.value = data.tipoUsuario;
      emailUsuarioDetalle.value = data.emailUsuario;
      profesionUsuarioDetalle.value = data.profesionUsuario;
      nroCelularDetalle.value = data.nroCelular;
      indUsuario.innerHTML = data.idEditar;
    });
}

///////////////////////////////////////////////
//////////////////  PREGUNTA 4 ////////////////
///////////////////////////////////////////////
function actualizarInformacionUsuario() {
  let profesionUsuarioDetalle = document.getElementById(
    "profesionUsuarioDetalle"
  );
  let nroCelularDetalle = document.getElementById("nroCelularDetalle");
  let indUsuario = document.getElementById("indUsuario");

  datos = {
    profesionUsuario: profesionUsuarioDetalle.value,
    nroCelular: nroCelularDetalle.value,
    idEditar: indUsuario.innerHTML,
  };
  console.log(datos);
  fetch(`/actualizarInfoUsuario`, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(datos),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      render(request, "informacionUsuario.html");
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
