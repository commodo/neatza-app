<?php

    function redirect($url, $statusCode = 303) {
        header('Location: ' . $url, true, $statusCode);
        die();
    }

    function endsWith($haystack, $needle) {
        // search forward starting from end minus needle length characters
        return $needle === "" || (($temp = strlen($haystack) - strlen($needle)) >= 0 && strpos($haystack, $needle, $temp) !== FALSE);
    }
    function append_line_to_file($line, $file) {
        $lines = file( $file, FILE_IGNORE_NEW_LINES);
        array_push( $lines, $line );
        file_put_contents( $file, implode("\n",$lines ) );
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
            redirect( '/' );
            exit( 0 );
        }
        return $img_url;
    }


    $img_url = "";
    $file_name = "";
    $files = scandir ( "../cache" );
    foreach ($files as $file) {
        if (endsWith( $file, ".moderate") ) {
            $lines = file( "../cache/" . $file, FILE_IGNORE_NEW_LINES);
            $img_url = do_post_action($file, $lines);
            break;
        }
    }

    if (count($_POST) > 0) {
        redirect( '/' );
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
<?php } else { ?>
    <h1>DONE</h1>
<?php } ?>
    </body>

</html>
