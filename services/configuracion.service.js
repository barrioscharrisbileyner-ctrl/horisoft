const configuracion = require("../data/configuracion");
const ParametroConfiguracion = require("../models/parametroConfiguracion.model");

class ConfiguracionService {

    obtenerTodos() {
        return configuracion;
    }

    obtenerPorClave(clave) {
        const parametro = configuracion.find(c => c.clave === clave);

        if (!parametro) {
            throw new Error("Parámetro de configuración no encontrado");
        }

        return parametro;
    }

    /**
     * Reglas de negocio:
     *  1. clave y valor son obligatorios.
     *  2. La clave debe ser única (no se permite duplicar parámetros).
     */
    crear(datos) {

        const { clave, valor, descripcion } = datos;

        if (!clave || valor === undefined) {
            throw new Error("clave y valor son obligatorios");
        }

        const claveDuplicada = configuracion.some(c => c.clave === clave);

        if (claveDuplicada) {
            throw new Error("Ya existe un parámetro con esa clave. Use PUT para actualizarlo.");
        }

        const nuevoParametro = new ParametroConfiguracion(clave, valor, descripcion || "");
        configuracion.push(nuevoParametro);

        return nuevoParametro;
    }

    actualizarValor(clave, valor) {

        if (valor === undefined) {
            throw new Error("El valor es obligatorio");
        }

        const parametro = this.obtenerPorClave(clave);
        parametro.valor = valor;

        return parametro;
    }

    eliminar(clave) {

        const indice = configuracion.findIndex(c => c.clave === clave);

        if (indice === -1) {
            throw new Error("Parámetro de configuración no encontrado");
        }

        configuracion.splice(indice, 1);
    }
}

module.exports = new ConfiguracionService();
