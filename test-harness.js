/**
 * Simula req/res de Express para poder ejercitar los controladores reales
 * (los mismos que usará Express) sin necesitar el paquete instalado.
 */
function mockRes() {
    return {
        statusCode: 200,
        body: null,
        status(code) { this.statusCode = code; return this; },
        json(obj) { this.body = obj; return this; },
    };
}

function llamar(nombre, controller, metodo, req) {
    const res = mockRes();
    controller[metodo](req, res);
    const icono = res.statusCode < 400 ? "✅" : "❌";
    console.log(`${icono} [${res.statusCode}] ${nombre}`);
    console.log(JSON.stringify(res.body, null, 2));
    console.log("");
    return res;
}

module.exports = { mockRes, llamar };
