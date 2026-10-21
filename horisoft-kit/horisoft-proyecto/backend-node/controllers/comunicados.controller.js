const comunicadosService = require("../services/comunicados.service");

class ComunicadosController {

    listar(req, res) {
        const soloPublicados = req.query.publicados === "true";
        res.json(comunicadosService.obtenerTodos(soloPublicados));
    }

    obtener(req, res) {
        try {
            res.json(comunicadosService.obtenerPorId(req.params.id));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const comunicado = comunicadosService.crear(req.body);
            res.status(201).json({ mensaje: "Comunicado publicado correctamente", comunicado });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    archivar(req, res) {
        try {
            const comunicado = comunicadosService.archivar(req.params.id);
            res.json(comunicado);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            comunicadosService.eliminar(req.params.id);
            res.json({ mensaje: "Comunicado eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new ComunicadosController();
