const configuracionService = require("../services/configuracion.service");

class ConfiguracionController {

    listar(req, res) {
        res.json(configuracionService.obtenerTodos());
    }

    obtener(req, res) {
        try {
            res.json(configuracionService.obtenerPorClave(req.params.clave));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const parametro = configuracionService.crear(req.body);
            res.status(201).json({ mensaje: "Parámetro creado correctamente", parametro });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    actualizarValor(req, res) {
        try {
            const parametro = configuracionService.actualizarValor(
                req.params.clave,
                req.body.valor
            );
            res.json(parametro);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            configuracionService.eliminar(req.params.clave);
            res.json({ mensaje: "Parámetro eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new ConfiguracionController();
