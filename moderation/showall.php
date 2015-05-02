<html>

    <head>
        <title>Moderation for the Neatza App</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link type="text/css" rel="stylesheet" href="index.css" media="all" />
    </head>

    <body>

    <form method='post'>
    <table>
<?php
    $lines = file( "../cache/group2.send", FILE_IGNORE_NEW_LINES);
    $count = 20;
    foreach ($lines as $line) {
?>
    <tr>
        <td>
            <?php echo $line ?> </br>
            <img src="<?php echo $line; ?>" />
        </td>
<?php } ?>
    </tr>
    </table>
    </form>

    </body>

</html>
