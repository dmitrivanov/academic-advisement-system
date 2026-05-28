<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

session_save_path(sys_get_temp_dir());
session_start();

require 'db.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username_input = trim($_POST['username'] ?? '');
    $password_input = $_POST['password'] ?? '';

    $stmt = $conn->prepare('SELECT * FROM users WHERE username = ?');
    $stmt->bind_param('s', $username_input);
    $stmt->execute();
    $user = $stmt->get_result()->fetch_assoc();

    if (
        $user &&
        (
            $password_input === $user['password_hash'] ||
            password_verify($password_input, $user['password_hash'])
        )
    ) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];

        if ($user['role'] === 'admin') {
            header('Location: admin.php');
            exit();
        }

        if ($user['role'] === 'judge') {
            header('Location: evaluate.php');
            exit();
        }

        $error = 'Unknown user role.';
    } else {
        $error = 'Invalid username or password.';
    }
}
?>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Login</title>
<link rel="stylesheet" href="style.css?v=5">
</head>

<body class="login-body">

<div class="login-card">
    <h1>Project Evaluation</h1>
    <h3>Judge/Admin Login</h3>

    <?php if ($error): ?>
        <p class="message"><?= htmlspecialchars($error) ?></p>
    <?php endif; ?>

    <form method="POST" action="index.php">
        <label>Username</label>
        <input type="text" name="username" required>

        <label>Password</label>
        <input type="password" name="password" required>

        <button type="submit">Login</button>
    </form>
</div>

</body>
</html>