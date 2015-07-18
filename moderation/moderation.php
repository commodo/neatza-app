<?php
    require_once("utils.php");

    $redirect_url = "/";
    $file = "";
    if (isset($_GET['group']) && file_exists("../cache/" . $_GET['group'])) {
        $file = $_GET['group'];
        $redirect_url = "/moderation.php?group=$file";
    }

    function do_post_action($file, $lines) {
        $file_send = "";
        $img_url = $lines[0];
        if (isset($_POST['approve']) || isset($_POST['discard'])) {
            if (isset($_POST['approve'])) {
                $send_file = "../cache/" . basename($file, '.moderate') . ".send";
                append_line_to_file($img_url, $send_file);
            }
            $lines = array_slice( $lines, 1 );
            file_put_contents( "../cache/" . $file, implode("\n",$lines ) );
            redirect( $redirect_url );
            exit( 0 );
        }
        return $img_url;
    }


    if (strlen($file) > 0) {
        $lines = file( "../cache/" . $file, FILE_IGNORE_NEW_LINES);
        $img_url = do_post_action($file, $lines);
    }

    if (count($_POST) > 0) {
        redirect( $redirect_url );
        return;
    }
?>

<html>

    <head>
        <title>Moderation for the Neatza App</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link type="text/css" rel="stylesheet" href="index.css" media="all" />
    </head>

    <body>

<?php if (strlen($img_url) > 0) { ?>
    <form method='post'>
    <table>
    <tr>
        <td><input id='approve' name='approve' type='submit' value='Approve' ></td>
        <td align='right'><input id='discard' name='discard' type='submit' value='Discard' ></td>
    </tr>
    <tr>
        <td colspan=2>
            <img src="<?php echo $img_url; ?>" />
        </td>
    </tr>
    </table>
    </form>
<?php } else if (strlen($file) == 0) { ?>
    <h1>Invalid file</h1>
<?php } else { ?>
    <h1>DONE</h1>
<?php } ?>
    </body>

</html>
