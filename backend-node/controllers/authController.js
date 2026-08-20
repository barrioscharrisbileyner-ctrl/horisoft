const authService = require("../services/authService");

class AuthController {

    listar(req, res) {
        res.json(authService.obtenerTodos());
    }

    obtener(req, res) {
        try {
            const { password, ...usuario } = authService.obtenerPorId(req.params.id);
            res.json(usuario);
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    registrar(req, res) {
        try {
            const usuario = authService.registrar(req.body);
            res.status(201).json({ mensaje: "Usuario registrado correctamente", usuario });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    login(req, res) {
        try {
            const { correo, password } = req.body;
            const { usuario, token } = authService.login(correo, password);
            res.json({
                mensaje: "¡Autenticación exitosa!",
                usuario,
                token: `Bearer ${token}`,
            });
        } catch (error) {
            res.status(401).json({ mensaje: error.message });
        }
    }

    perfil(req, res) {
        // req.usuario lo agrega el middleware authMiddleware.js tras validar el token.
        res.json({ mensaje: "Token válido", usuario: req.usuario });
    }

    actualizarRol(req, res) {
        try {
            const usuario = authService.actualizarRol(req.params.id, req.body.rol);
            res.json(usuario);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    actualizarEstado(req, res) {
        try {
            const usuario = authService.actualizarEstado(req.params.id, req.body.estado);
            res.json(usuario);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            authService.eliminar(req.params.id);
            res.json({ mensaje: "Usuario eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new AuthController();
